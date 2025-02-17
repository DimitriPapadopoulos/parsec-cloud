// Parsec Cloud (https://parsec.cloud) Copyright (c) BUSL-1.1 (eventually AGPL-3.0) 2016-present Scille SAS

use base64::prelude::{Engine, BASE64_STANDARD};
use chrono::{DateTime, FixedOffset};
use http_body::Full;
use hyper::{
    body::{self, Bytes},
    header::{AUTHORIZATION, WWW_AUTHENTICATE},
    service::Service,
    Body, HeaderMap, Request, Response, StatusCode,
};
use libparsec_client_connection::{API_VERSION_HEADER_NAME, PARSEC_AUTH_METHOD};
use libparsec_crypto::VerifyKey;
use libparsec_protocol::authenticated_cmds::v3::{self as authenticated_cmds, AnyCmdReq};
use libparsec_types::DeviceID;
use std::{
    collections::HashMap,
    convert::Infallible,
    future::Future,
    ops::Deref,
    pin::Pin,
    str::FromStr,
    task::{Context, Poll},
};

pub type ID = DeviceID;

#[derive(Debug)]
pub struct AuthRequest {
    verify_key: VerifyKey,
    signature_b64: String,
}

pub struct SignatureVerifier {
    registered_public_keys: HashMap<ID, VerifyKey>,
}

impl SignatureVerifier {
    pub fn new(registered_public_keys: HashMap<ID, VerifyKey>) -> Self {
        Self {
            registered_public_keys,
        }
    }

    fn get_auth_request(&self, headers: &HeaderMap) -> Result<AuthRequest, anyhow::Error> {
        parse_headers(headers).and_then(|(raw_author, _timestamp, raw_signature)| {
            let (_author, verify_key) = BASE64_STANDARD
                .decode(raw_author)
                .map_err(anyhow::Error::from)
                .and_then(|bytes| {
                    String::from_utf8(bytes)
                        .map_err(anyhow::Error::from)
                        .and_then(|author| {
                            let id = ID::from_str(&author).map_err(|e| {
                                anyhow::anyhow!(r#"failed to parse device id "{e}""#)
                            })?;
                            if let Some(vk) = self.registered_public_keys.get(&id) {
                                Ok((author, vk.clone()))
                            } else {
                                anyhow::bail!("author {author} not found")
                            }
                        })
                })?;
            Ok(AuthRequest {
                verify_key,
                signature_b64: raw_signature,
            })
        })
    }
}

impl Service<Request<Body>> for SignatureVerifier {
    type Response = Response<Full<Bytes>>;
    type Error = anyhow::Error;
    type Future = Pin<Box<dyn Future<Output = Result<Self::Response, Self::Error>> + Send>>;

    fn poll_ready(&mut self, _cx: &mut Context<'_>) -> Poll<Result<(), Self::Error>> {
        // The service is directly available.
        Poll::Ready(Ok(()))
    }

    fn call(&mut self, req: Request<Body>) -> Self::Future {
        log::debug!("server recv request");
        let headers = req.headers();
        let api_version = headers.get(API_VERSION_HEADER_NAME).map(|v| {
            v.to_str()
                .expect("cannot decode api_version header")
                .to_string()
        });
        log::debug!("api_version: {api_version:?}");
        let res = self.get_auth_request(headers);
        log::debug!("parsed header: {res:?}");

        let fut = async move {
            anyhow::ensure!(
                api_version == Some(libparsec_protocol::API_VERSION.to_string()),
                "Missing or Invalid API_VERSION header"
            );
            let auth_req = res?;
            let body = body::to_bytes(req.into_body()).await?;

            let signature = BASE64_STANDARD.decode(auth_req.signature_b64)?;
            let signed_message = rebuild_signed_message(signature, &body);
            if let Err(e) = auth_req.verify_key.verify(&signed_message) {
                log::error!("invalid signed request: {e}");
                return Ok(Response::builder()
                    .status(StatusCode::UNAUTHORIZED)
                    .header(WWW_AUTHENTICATE, PARSEC_AUTH_METHOD)
                    .body(Full::from(Bytes::from_static(b"invalid signed request")))?);
            }

            let cmd = authenticated_cmds::AnyCmdReq::load(body.as_ref())
                .map_err(|e| anyhow::anyhow!("{e}"))?;
            let ping_req = if let AnyCmdReq::Ping(req) = cmd {
                req
            } else {
                anyhow::bail!("mock server only support ping command")
            };
            let ping_rep = authenticated_cmds::ping::Rep::Ok {
                pong: format!(
                    "hello from the server side!, thanks for your message: \"{}\"",
                    ping_req.ping
                ),
            };

            let rep_body = ping_rep
                .dump()
                .map_err(|e| anyhow::anyhow!("{e}"))
                .map(|bytes| Full::from(Bytes::from(bytes)))?;

            Ok(Response::builder().status(StatusCode::OK).body(rep_body)?)
        };
        Box::pin(fut)
    }
}

fn rebuild_signed_message(signature: Vec<u8>, body: &Bytes) -> Vec<u8> {
    Vec::from_iter(signature.iter().chain(body.deref()).copied())
}

fn parse_headers(headers: &HeaderMap) -> anyhow::Result<(String, DateTime<FixedOffset>, String)> {
    match headers.get(AUTHORIZATION) {
        Some(value) => {
            if Some(PARSEC_AUTH_METHOD) != value.to_str().ok() {
                anyhow::bail!("invalid authorization header")
            }
        }
        _ => anyhow::bail!("missing authorization header"),
    }
    let raw_user_id = headers
        .get("Author")
        .ok_or_else(|| anyhow::anyhow!("missing author header"))?
        .to_str()
        .map_err(anyhow::Error::from)?
        .to_string();

    let raw_timestamp = headers
        .get("Timestamp")
        .ok_or_else(|| anyhow::anyhow!("missing timestamp header"))?
        .to_str()
        .map_err(anyhow::Error::from)?;
    let timestamp = DateTime::parse_from_rfc3339(raw_timestamp)?;

    if timestamp.timestamp_subsec_millis() == 0 {
        log::warn!("timestamp should have defined the millisecond (raw: {raw_timestamp})")
    }

    let raw_signature = headers
        .get("Signature")
        .ok_or_else(|| anyhow::anyhow!("missing signature header"))?
        .to_str()
        .map_err(anyhow::Error::from)?
        .to_string();

    Ok((raw_user_id, timestamp, raw_signature))
}

#[derive(Default)]
pub struct MakeSignatureVerifier {
    registered_public_keys: HashMap<ID, VerifyKey>,
}

impl MakeSignatureVerifier {
    pub fn register_public_key(&mut self, id: ID, key: VerifyKey) {
        self.registered_public_keys.insert(id, key);
    }
}

impl<T> Service<T> for MakeSignatureVerifier {
    type Response = SignatureVerifier;
    type Error = Infallible;
    type Future = Pin<Box<dyn Future<Output = Result<Self::Response, Self::Error>> + Send>>;

    fn poll_ready(&mut self, _cx: &mut Context<'_>) -> Poll<Result<(), Self::Error>> {
        Poll::Ready(Ok(()))
    }

    fn call(&mut self, _req: T) -> Self::Future {
        let registered_public_keys = self.registered_public_keys.clone();
        let fut = async move { Ok(SignatureVerifier::new(registered_public_keys)) };
        Box::pin(fut)
    }
}
