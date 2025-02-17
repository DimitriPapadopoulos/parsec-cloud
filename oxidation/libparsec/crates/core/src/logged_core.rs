// Parsec Cloud (https://parsec.cloud) Copyright (c) BUSL-1.1 (eventually AGPL-3.0) 2016-present Scille SAS

use libparsec_client_types::LocalDevice;
use libparsec_types::DeviceID;

#[derive(Debug, Clone)]
pub struct LoggedCore {
    pub device: LocalDevice,
}

impl LoggedCore {
    pub fn device_id(&self) -> &DeviceID {
        &self.device.device_id
    }
}
