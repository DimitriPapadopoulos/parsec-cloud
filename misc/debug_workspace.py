#! /usr/bin/env python3

import os
import trio

from tqdm import tqdm
from humanize import naturalsize

from parsec.logging import configure_logging
from parsec.core.logged_core import logged_core_factory
from parsec.core.config import get_default_config_dir, load_config
from parsec.core.local_device import list_available_devices, load_device_with_password


LOG_LEVEL = "WARNING"
DEVICE_ID = "alice@laptop"
PASSWORD = "test"


async def main():

    # Config
    configure_logging(LOG_LEVEL)
    config_dir = get_default_config_dir(os.environ)
    config = load_config(config_dir)
    devices = list_available_devices(config_dir)
    key_file = next(key_file for _, device_id, _, key_file in devices if device_id == DEVICE_ID)
    device = load_device_with_password(key_file, PASSWORD)

    # Log in
    async with logged_core_factory(config, device) as core:

        # Get workspace
        user_manifest = core.user_fs.get_user_manifest()
        workspace_entry = user_manifest.workspaces[0]
        workspace = core.user_fs.get_workspace(workspace_entry.id)

        # Touch file
        path = "/foo"
        block_size = 512 * 1024
        file_size = 64 * 1024 * 1024
        await workspace.touch(path)
        info = await workspace.path_info(path)

        # Log
        print(f"{device.device_id} | {workspace_entry.name} | {path}")

        # Write file
        start = info["size"] // block_size
        stop = file_size // block_size
        for i in tqdm(range(start, stop)):
            await workspace.write_bytes(path, b"\x00" * block_size, offset=i * block_size)

        # Sync
        await workspace.sync()

        # Serialize
        manifest = workspace.local_storage.get_manifest(info["id"])
        raw = manifest.dump()

        # Printout
        print(f"File size: {naturalsize(file_size)}")
        print(f"Manifest size: {naturalsize(len(raw))}")

        # Let sync monitor finish
        await trio.sleep(2)

        # Debug
        # breakpoint()
        # manifest


if __name__ == "__main__":
    trio.run(main)
