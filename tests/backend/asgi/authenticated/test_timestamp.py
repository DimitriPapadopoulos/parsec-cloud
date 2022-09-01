# Parsec Cloud (https://parsec.cloud) Copyright (c) AGPL-3.0 2016-present Scille SAS

import pytest

from tests.common.backend import AuthenticatedHttpApiClient


@pytest.mark.trio
async def test_timestamp_missing_header(alice_http_client: AuthenticatedHttpApiClient):
    rep = await alice_http_client.send_dummy_request(
        extra_headers={"timestamp": None}, check_rep=False
    )
    assert rep.status_code == 400  # bad request
