// Parsec Cloud (https://parsec.cloud) Copyright (c) BSLv1.1 (eventually AGPLv3) 2016-2021 Scille SAS

#[macro_use]
extern crate lazy_static;

mod addr;
mod certif;
pub mod data_macros;
mod ext_types;
mod id;
mod invite;
mod manifest;
mod message;
mod protocol;

pub use addr::*;
pub use certif::*;
pub use ext_types::*;
pub use id::*;
pub use invite::*;
pub use manifest::*;
pub use message::*;
pub use protocol::*;

#[macro_export]
macro_rules! set {
    {$($v: expr),* $(,)?} => ({
        use std::iter::{Iterator, IntoIterator};
        Iterator::collect(IntoIterator::into_iter([$($v,)*]))
    });
}

#[macro_export]
macro_rules! map {
    {$($k: expr => $v: expr),* $(,)?} => ({
        use std::iter::{Iterator, IntoIterator};
        Iterator::collect(IntoIterator::into_iter([$(($k, $v),)*]))
    });
}
