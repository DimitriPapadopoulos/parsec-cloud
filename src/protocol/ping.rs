// Parsec Cloud (https://parsec.cloud) Copyright (c) BUSL-1.1 (eventually AGPL-3.0) 2016-present Scille SAS

use pyo3::{
    exceptions::PyNotImplementedError,
    import_exception,
    prelude::*,
    types::{PyBytes, PyString},
};

use libparsec::protocol::{authenticated_cmds, invited_cmds};

use crate::protocol::gen_rep;

import_exception!(parsec.api.protocol, ProtocolError);

#[pyclass]
#[derive(PartialEq, Clone)]
pub(crate) struct InvitedPingReq(pub invited_cmds::ping::Req);

#[pymethods]
impl InvitedPingReq {
    #[new]
    fn new(ping: String) -> PyResult<Self> {
        Ok(Self(invited_cmds::ping::Req { ping }))
    }

    fn __repr__(&self) -> PyResult<String> {
        Ok(format!("{:?}", self.0))
    }

    fn dump<'py>(&self, py: Python<'py>) -> PyResult<&'py PyBytes> {
        Ok(PyBytes::new(
            py,
            &self.0.clone().dump().map_err(ProtocolError::new_err)?,
        ))
    }

    #[getter]
    fn ping(&self) -> PyResult<&str> {
        Ok(&self.0.ping)
    }
}

gen_rep!(invited_cmds::ping, InvitedPingRep, { .. });

#[pyclass(extends=InvitedPingRep)]
pub(crate) struct InvitedPingRepOk;

#[pymethods]
impl InvitedPingRepOk {
    #[new]
    fn new(pong: String) -> PyResult<(Self, InvitedPingRep)> {
        Ok((Self, InvitedPingRep(invited_cmds::ping::Rep::Ok { pong })))
    }

    #[getter]
    fn pong<'py>(_self: PyRef<'py, Self>, py: Python<'py>) -> PyResult<&'py PyString> {
        Ok(match &_self.as_ref().0 {
            invited_cmds::ping::Rep::Ok { pong, .. } => PyString::new(py, pong),
            _ => return Err(PyNotImplementedError::new_err("")),
        })
    }
}

#[pyclass]
#[derive(PartialEq, Clone)]
pub(crate) struct AuthenticatedPingReq(pub authenticated_cmds::ping::Req);

#[pymethods]
impl AuthenticatedPingReq {
    #[new]
    fn new(ping: String) -> PyResult<Self> {
        Ok(Self(authenticated_cmds::ping::Req { ping }))
    }

    fn __repr__(&self) -> PyResult<String> {
        Ok(format!("{:?}", self.0))
    }

    fn dump<'py>(&self, py: Python<'py>) -> PyResult<&'py PyBytes> {
        Ok(PyBytes::new(
            py,
            &self.0.clone().dump().map_err(ProtocolError::new_err)?,
        ))
    }

    #[getter]
    fn ping(&self) -> PyResult<&str> {
        Ok(&self.0.ping)
    }
}

gen_rep!(authenticated_cmds::ping, AuthenticatedPingRep, { .. });

#[pyclass(extends=AuthenticatedPingRep)]
pub(crate) struct AuthenticatedPingRepOk;

#[pymethods]
impl AuthenticatedPingRepOk {
    #[new]
    fn new(pong: String) -> PyResult<(Self, AuthenticatedPingRep)> {
        Ok((
            Self,
            AuthenticatedPingRep(authenticated_cmds::ping::Rep::Ok { pong }),
        ))
    }

    #[getter]
    fn pong<'py>(_self: PyRef<'py, Self>, py: Python<'py>) -> PyResult<&'py PyString> {
        Ok(match &_self.as_ref().0 {
            authenticated_cmds::ping::Rep::Ok { pong, .. } => PyString::new(py, pong),
            _ => return Err(PyNotImplementedError::new_err("")),
        })
    }
}
