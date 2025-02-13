// Parsec Cloud (https://parsec.cloud) Copyright (c) BUSL-1.1 (eventually AGPL-3.0) 2016-present Scille SAS
//! Module that wrap an [diesel::SqliteConnection] behind a executor to allow to have an async manner to executor sql queries.

use std::thread::JoinHandle;

use diesel::{connection::SimpleConnection, SqliteConnection};
use libparsec_platform_async::channel;

use crate::{DatabaseError, DatabaseResult};

/// The executor that manage and send job to the background executor.
pub(crate) struct SqliteExecutor {
    /// The channel that will be used to send job to the background executor.
    job_sender: Option<channel::Sender<Operation>>,
    /// The handle to the [BackgroundSqliteExecutor].
    handle: Option<JoinHandle<()>>,
}

/// A list of operation that can be executed on the background executor.
enum Operation {
    /// Operate a full vacuum, meaning executing `VACUUM` on the sqlite connection
    /// and re-opening the connection to force cleanup of the driver.
    FullVacuum(channel::Sender<DatabaseResult<()>>),
    /// Execute a standard job.
    Job(JobFunc),
}

/// A type alias for function that will be sent to the background executor.
type JobFunc = Box<dyn FnOnce(&mut SqliteConnection) + Send>;

impl SqliteExecutor {
    /// Spawn the executor in a thread.
    pub fn spawn<F>(connection: SqliteConnection, reopen_connection: F) -> Self
    where
        F: Send + (Fn(SqliteConnection) -> DatabaseResult<SqliteConnection>) + 'static,
    {
        // Flume's channel doesn't drop the queue's content when the receiver is
        // dropped. This has unexpected consequences if the queue contains a sender
        // we are waiting on somewhere else (and yes, this is precisely what we have
        // here !)
        // So the solution is to have a zero-size-bonded queue, this way the queue is
        // just a rendez-vous point and never contains anything.
        // (see https://github.com/zesterer/flume/issues/89)
        let (job_sender, job_receiver) = channel::bounded(0);
        let background_executor = BackgroundSqliteExecutor {
            job_receiver,
            connection,
        };
        // TODO: currently if the thread panic the error is printed to stderr,
        // we should instead have a proper panic handler that log an error
        let handle = std::thread::Builder::new()
            .name("SqliteExecutor".to_string())
            .spawn(move || background_executor.serve(reopen_connection))
            .expect("failed to spawn thread");

        Self {
            job_sender: Some(job_sender),
            handle: Some(handle),
        }
    }

    /// Execute the provided closure to execute a query on the sqlite connection.
    /// Will return the result when finished.
    pub fn exec<F, R>(&self, job: F) -> ExecJob<R>
    where
        F: (FnOnce(&mut SqliteConnection) -> R) + Send + 'static,
        R: Send + 'static,
    {
        // We use a bounded queue with a size of 1 to receive the result from
        // the background executor.
        // We don't use a rendez-vous point (i.e. size of 0) because the background
        // executor doesn't care about us and just want to move on processing the next
        // job. On top of that there is no risk of deadlock if the receiver gets dropped
        // because the queue contains opaque data from the background executor point of
        // view (i.e. it cannot have an await depending on data it doesn't understand !).
        let (tx, rx) = channel::bounded::<R>(1);
        let wrapped_job = move |conn: &mut SqliteConnection| {
            let res = job(conn);
            // If send fails it means the caller's future has been dropped
            // (hence dropping `rx`). In theory there is nothing wrong about
            // it, however we log it anyway given the caller's unexpected drop
            // may also be the sign of a bug...
            if tx.send(res).is_err() {
                log::warn!("Caller has left");
            }
        };
        let wrapped_job = Box::new(wrapped_job);

        let sender = self
            .job_sender
            .as_ref()
            .expect("Job sender cannot be none before calling `drop`");

        ExecJob {
            job: Operation::Job(wrapped_job),
            sender: sender.clone(),
            result_recv: rx,
        }
    }

    /// Run a full vacuum, meaning that it will execute a standar vacuum and re-open the database connection to force cleanup.
    pub fn full_vacuum(&self) -> ExecJob<DatabaseResult<()>> {
        let (tx, rx) = channel::bounded(1);
        ExecJob {
            job: Operation::FullVacuum(tx),
            sender: self
                .job_sender
                .as_ref()
                .expect("Job sender cannot be none before calling `drop`")
                .clone(),
            result_recv: rx,
        }
    }
}

/// The structure generated by [SqliteExecutor::exec].
/// You need to call [ExecJob::send] to effectively execute the job.
#[must_use]
pub(crate) struct ExecJob<R>
where
    R: Send + 'static,
{
    /// The job to execute
    job: Operation,
    /// The channel to send the job to.
    sender: channel::Sender<Operation>,
    /// The channel that will receive the result of the job.
    result_recv: channel::Receiver<R>,
}

impl<R> ExecJob<R>
where
    R: Send + 'static,
{
    /// Send the job to the background executor and return the result when it finish.
    pub async fn send(self) -> DatabaseResult<R> {
        let ExecJob {
            job,
            sender,
            result_recv,
        } = self;

        sender
            .send_async(job)
            .await
            .map_err(|_| DatabaseError::Closed)?;
        drop(sender);

        result_recv
            .recv_async()
            .await
            .map_err(|_| DatabaseError::Closed)
    }
}

impl Drop for SqliteExecutor {
    fn drop(&mut self) {
        drop(self.job_sender.take());
        if let Some(handle) = self.handle.take() {
            // An error is returned in case the joined thread has panicked
            // We can ignore the error given it should have already been
            // logged as part of the panic handling system.
            let _ = handle.join();
        }
    }
}

/// The background executor that manage the sqlite connection on a separated thread.
struct BackgroundSqliteExecutor {
    /// The channel that will receive job to execute.
    job_receiver: channel::Receiver<Operation>,
    /// The connection to the sqlite database.
    connection: SqliteConnection,
}

impl BackgroundSqliteExecutor {
    /// Start the background executor to listen for incoming jobs.
    /// This method will stop when all sender channel are closed and no more job are present on the channel queue.
    fn serve<F>(self, reopen_connection: F)
    where
        F: Fn(SqliteConnection) -> DatabaseResult<SqliteConnection>,
    {
        let BackgroundSqliteExecutor {
            job_receiver,
            mut connection,
        } = self;
        for operation in job_receiver.into_iter() {
            match operation {
                Operation::FullVacuum(res_tx) => {
                    // Run a full vacuum, meaning that it will execute a standar vacuum
                    // and re-open the database connection to force cleanup.
                    let res = connection
                        .batch_execute("VACUUM")
                        .map_err(DatabaseError::from)
                        .and_then(|_| reopen_connection(connection));

                    match res {
                        Ok(conn) => {
                            connection = conn;
                            res_tx
                                .send(Ok(()))
                                .expect("Failed to send the result of the full vacuum operation");
                        }
                        // Oh no, we have an error, the background executor will stop just after notifying the caller.
                        Err(err) => {
                            log::warn!("Full vacuum has failed: {:?}", &err);
                            res_tx
                                .send(Err(err))
                                .expect("Failed to send the result of the full vacuum operation");
                            return;
                        }
                    }
                }
                Operation::Job(job) => job(&mut connection),
            }
        }
        log::info!("BackgroundSqliteExecutor finished all his jobs");
    }
}

#[cfg(test)]
mod tests {
    use crate::DatabaseError;
    use diesel::{connection::SimpleConnection, Connection, SqliteConnection};
    use rstest::rstest;

    use super::SqliteExecutor;

    #[rstest]
    #[test_log::test(tokio::test)]
    async fn fail_reopen_database() {
        let connection = SqliteConnection::establish(":memory:").unwrap();
        let executor = SqliteExecutor::spawn(connection, |_conn| Err(crate::DatabaseError::Closed));

        // Basic SQL query to see if the Executor is working properly.
        executor
            .exec(|conn| conn.batch_execute("SELECT 1"))
            .send()
            .await
            .unwrap()
            .unwrap();

        let err = executor.full_vacuum().send().await.unwrap().unwrap_err();

        // TODO: Check that we've outputted a log warning saying we failed to reopen the database connection.
        assert_eq!(err, DatabaseError::Closed);

        // Because `full_vacuum` failed, the executor should be closed.
        let err = executor
            .exec(|conn| conn.batch_execute("SELECT 1"))
            .send()
            .await
            .unwrap_err();

        assert_eq!(err, DatabaseError::Closed);
    }
}
