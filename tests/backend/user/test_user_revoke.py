# Parsec Cloud (https://parsec.cloud) Copyright (c) AGPL-3.0 2016-present Scille SAS

from parsec.backend.backend_events import BackendEvent
import pytest
import trio
from pendulum import now as pendulum_now, datetime

from quart.testing.connections import WebsocketDisconnectError

from parsec.backend.user import INVITATION_VALIDITY
from parsec.api.data import RevokedUserCertificateContent, UserProfile
from parsec.api.protocol import HandshakeRevokedDevice

from tests.common import freeze_time
from tests.backend.common import user_revoke, ping


@pytest.mark.trio
async def test_backend_close_on_user_revoke(
    backend_asgi_app, alice_ws, backend_authenticated_ws_factory, bob, alice
):
    now = pendulum_now()
    bob_revocation = RevokedUserCertificateContent(
        author=alice.device_id, timestamp=now, user_id=bob.user_id
    ).dump_and_sign(alice.signing_key)

    async with backend_authenticated_ws_factory(backend_asgi_app, bob) as bob_ws:
        with backend_asgi_app.backend.event_bus.listen() as spy:
            rep = await user_revoke(alice_ws, revoked_user_certificate=bob_revocation)
            assert rep == {"status": "ok"}
            await spy.wait_with_timeout(
                BackendEvent.USER_REVOKED,
                {"organization_id": bob.organization_id, "user_id": bob.user_id},
            )
            # `user.revoked` event schedules connection cancellation, so wait
            # for things to settle down to make sure the cancellation is done
            await trio.testing.wait_all_tasks_blocked()
        # Bob cannot send new command
        with pytest.raises(WebsocketDisconnectError):
            await ping(bob_ws)


@pytest.mark.trio
async def test_user_revoke_ok(
    backend_asgi_app, backend_authenticated_ws_factory, adam_ws, alice, adam
):
    now = pendulum_now()
    alice_revocation = RevokedUserCertificateContent(
        author=adam.device_id, timestamp=now, user_id=alice.user_id
    ).dump_and_sign(adam.signing_key)

    with backend_asgi_app.backend.event_bus.listen() as spy:
        rep = await user_revoke(adam_ws, revoked_user_certificate=alice_revocation)
        assert rep == {"status": "ok"}
        await spy.wait_with_timeout(
            BackendEvent.USER_REVOKED,
            {"organization_id": alice.organization_id, "user_id": alice.user_id},
        )

    # Alice cannot connect from now on...
    with pytest.raises(HandshakeRevokedDevice):
        async with backend_authenticated_ws_factory(backend_asgi_app, alice):
            pass


@pytest.mark.trio
async def test_user_revoke_not_admin(
    backend_asgi_app, backend_authenticated_ws_factory, bob_ws, alice, bob
):
    now = pendulum_now()
    alice_revocation = RevokedUserCertificateContent(
        author=bob.device_id, timestamp=now, user_id=alice.user_id
    ).dump_and_sign(bob.signing_key)

    rep = await user_revoke(bob_ws, revoked_user_certificate=alice_revocation)
    assert rep == {"status": "not_allowed", "reason": "User `bob` is not admin"}


@pytest.mark.trio
async def test_cannot_self_revoke(
    backend_asgi_app, backend_authenticated_ws_factory, alice_ws, alice
):
    now = pendulum_now()
    alice_revocation = RevokedUserCertificateContent(
        author=alice.device_id, timestamp=now, user_id=alice.user_id
    ).dump_and_sign(alice.signing_key)

    rep = await user_revoke(alice_ws, revoked_user_certificate=alice_revocation)
    assert rep == {"status": "not_allowed", "reason": "Cannot do self-revocation"}


@pytest.mark.trio
async def test_user_revoke_unknown(backend_asgi_app, alice_ws, alice, mallory):
    revoked_user_certificate = RevokedUserCertificateContent(
        author=alice.device_id, timestamp=pendulum_now(), user_id=mallory.user_id
    ).dump_and_sign(alice.signing_key)

    rep = await user_revoke(alice_ws, revoked_user_certificate=revoked_user_certificate)
    assert rep == {"status": "not_found"}


@pytest.mark.trio
async def test_user_revoke_already_revoked(backend_asgi_app, alice_ws, bob, alice):
    now = pendulum_now()
    bob_revocation = RevokedUserCertificateContent(
        author=alice.device_id, timestamp=now, user_id=bob.user_id
    ).dump_and_sign(alice.signing_key)

    rep = await user_revoke(alice_ws, revoked_user_certificate=bob_revocation)
    assert rep["status"] == "ok"

    rep = await user_revoke(alice_ws, revoked_user_certificate=bob_revocation)
    assert rep == {"status": "already_revoked", "reason": f"User `{bob.user_id}` already revoked"}


@pytest.mark.trio
async def test_user_revoke_invalid_certified(backend_asgi_app, alice_ws, alice2, bob):
    revoked_user_certificate = RevokedUserCertificateContent(
        author=alice2.device_id, timestamp=pendulum_now(), user_id=bob.user_id
    ).dump_and_sign(alice2.signing_key)

    rep = await user_revoke(alice_ws, revoked_user_certificate=revoked_user_certificate)
    assert rep == {
        "status": "invalid_certification",
        "reason": "Invalid certification data (Signature was forged or corrupt).",
    }


@pytest.mark.trio
async def test_user_revoke_certify_too_old(backend_asgi_app, alice_ws, alice, bob):
    now = datetime(2000, 1, 1)
    revoked_user_certificate = RevokedUserCertificateContent(
        author=alice.device_id, timestamp=now, user_id=bob.user_id
    ).dump_and_sign(alice.signing_key)

    with freeze_time(now.add(seconds=INVITATION_VALIDITY + 1)):
        rep = await user_revoke(alice_ws, revoked_user_certificate=revoked_user_certificate)
        assert rep == {
            "status": "invalid_certification",
            "reason": "Invalid timestamp in certification.",
        }


@pytest.mark.trio
async def test_user_revoke_other_organization(
    ws_from_other_organization_factory,
    backend_authenticated_ws_factory,
    backend_asgi_app,
    alice,
    bob,
):
    # Organizations should be isolated even for organization admins
    async with ws_from_other_organization_factory(
        backend_asgi_app, mimick=alice.device_id, profile=UserProfile.ADMIN
    ) as sock:

        revocation = RevokedUserCertificateContent(
            author=sock.device.device_id, timestamp=pendulum_now(), user_id=bob.user_id
        ).dump_and_sign(sock.device.signing_key)

        rep = await user_revoke(sock, revoked_user_certificate=revocation)
        assert rep == {"status": "not_found"}

    # Make sure bob still works
    async with backend_authenticated_ws_factory(backend_asgi_app, bob):
        pass
