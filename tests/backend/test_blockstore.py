import pytest

from parsec.utils import to_jsonb64

from tests.common import connect_backend


def _get_existing_block(backend):
    # Backend must have been populated before that
    return list(backend.test_populate_data['blocks'].items())[0]


@pytest.mark.trio
async def test_blockstore_get_url(alice_backend_sock):
    await alice_backend_sock.send({'cmd': 'blockstore_get_url'})
    rep = await alice_backend_sock.recv()
    assert rep == {'status': 'ok', 'url': 'backend://'}


@pytest.mark.trio
async def test_blockstore_post_and_get(backend):
    async with connect_backend(backend, auth_as='alice@test') as sock:
        block = to_jsonb64(b'Hodi ho !')
        await sock.send({'cmd': 'blockstore_post', 'block': block})
        rep = await sock.recv()
    assert rep['status'] == 'ok'
    assert rep['id']

    async with connect_backend(backend, auth_as='bob@test') as sock:
        await sock.send({'cmd': 'blockstore_get', 'id': rep['id']})
        rep = await sock.recv()
    assert rep == {'status': 'ok', 'block': block}


@pytest.mark.parametrize('bad_msg', [
    {},
    {'blob': to_jsonb64(b'...'), 'bad_field': 'foo'},
    {'blob': 42},
    {'blob': None},
    {'id': '123', 'blob': to_jsonb64(b'...')},
])
@pytest.mark.trio
async def test_blockstore_post_bad_msg(alice_backend_sock, bad_msg):
    await alice_backend_sock.send({'cmd': 'blockstore_post', **bad_msg})
    rep = await alice_backend_sock.recv()
    assert rep['status'] == 'bad_message'


@pytest.mark.trio
async def test_blockstore_get_not_found(alice_backend_sock):
    await alice_backend_sock.send({'cmd': 'blockstore_get', 'id': '1234'})
    rep = await alice_backend_sock.recv()
    assert rep == {'status': 'block_not_found', 'reason': 'Unknown block id.'}


@pytest.mark.parametrize('bad_msg', [
    {'id': '1234', 'bad_field': 'foo'},
    {'id': 42},
    {'id': None},
    {}
])
@pytest.mark.trio
async def test_blockstore_get_bad_msg(alice_backend_sock, bad_msg):
    await alice_backend_sock.send({'cmd': 'blockstore_get', **bad_msg})
    rep = await alice_backend_sock.recv()
    # Id and trust_seed are invalid anyway, but here we test another layer
    # so it's not important as long as we get our `bad_message` status
    assert rep['status'] == 'bad_message'
