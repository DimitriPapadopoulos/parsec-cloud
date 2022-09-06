# Parsec Cloud (https://parsec.cloud) Copyright (c) AGPL-3.0 2016-present Scille SAS

from typing import Type

from parsec._parsec import (
    VlobID,
    VlobCreateReq,
    VlobCreateRep,
    VlobReadReq,
    VlobReadRep,
    VlobUpdateReq,
    VlobUpdateRep,
    VlobPollChangesReq,
    VlobPollChangesRep,
    VlobListVersionsReq,
    VlobListVersionsRep,
    VlobMaintenanceGetReencryptionBatchReq,
    VlobMaintenanceGetReencryptionBatchRep,
    VlobMaintenanceSaveReencryptionBatchReq,
    VlobMaintenanceSaveReencryptionBatchRep,
)
from parsec.serde import fields
from parsec.api.protocol.base import BaseRepSchema, ApiCommandSerializer

__all__ = (
    "VlobID",
    "VlobIDField",
    "vlob_create_serializer",
    "vlob_read_serializer",
    "vlob_update_serializer",
    "vlob_poll_changes_serializer",
    "vlob_list_versions_serializer",
    "vlob_maintenance_get_reencryption_batch_serializer",
    "vlob_maintenance_save_reencryption_batch_serializer",
)


VlobIDField: Type[fields.Field] = fields.uuid_based_field_factory(VlobID)


class SequesterInconsistencyRepSchema(BaseRepSchema):
    """
    This schema has been added to API version 2.8/3.2 (Parsec v2.11.0).
    """

    status = fields.CheckedConstant("sequester_inconsistency", required=True)
    sequester_authority_certificate = fields.Bytes(required=True, allow_none=False)
    sequester_services_certificates = fields.List(fields.Bytes(), required=True, allow_none=False)


vlob_create_serializer = ApiCommandSerializer(VlobCreateReq, VlobCreateRep)
vlob_read_serializer = ApiCommandSerializer(VlobReadReq, VlobReadRep)
vlob_update_serializer = ApiCommandSerializer(VlobUpdateReq, VlobUpdateRep)
vlob_poll_changes_serializer = ApiCommandSerializer(VlobPollChangesReq, VlobPollChangesRep)
vlob_list_versions_serializer = ApiCommandSerializer(VlobListVersionsReq, VlobListVersionsRep)
# Maintenance stuff
vlob_maintenance_get_reencryption_batch_serializer = ApiCommandSerializer(
    VlobMaintenanceGetReencryptionBatchReq, VlobMaintenanceGetReencryptionBatchRep
)
vlob_maintenance_save_reencryption_batch_serializer = ApiCommandSerializer(
    VlobMaintenanceSaveReencryptionBatchReq, VlobMaintenanceSaveReencryptionBatchRep
)
