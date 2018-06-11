import pytest
import trio
import attr
from collections import defaultdict
from random import randrange, choice
from string import ascii_lowercase

from parsec.core.fs import FSInvalidPath


FUZZ_PARALLELISM = 10
FUZZ_TIME = 10.


def generate_name():
    return "".join([choice(ascii_lowercase) for x in range(4)])


@attr.s
class FSState:
    stats = defaultdict(lambda: defaultdict(lambda: 0))
    files = attr.ib(factory=list)
    folders = attr.ib(factory=lambda: ["/"])

    def get_cooked_stats(self):
        stats = {}
        for fuzzer_stat in self.stats.values():
            for k, v in fuzzer_stat.items():
                try:
                    stats[k] += v
                except KeyError:
                    stats[k] = v
        total = sum(stats.values())
        return sorted([(k, (v * 100 // total)) for k, v in stats.items()], key=lambda x: -x[1])

    def add_stat(self, fuzzer_id, type):
        self.stats[fuzzer_id][type] += 1

    def get_folder(self):
        return self.folders[randrange(0, len(self.folders))].replace("//", "/")

    def get_file(self):
        if not self.files:
            raise SkipCommand()
        return self.files[randrange(0, len(self.files))].replace("//", "/")

    def get_path(self):
        if self.files and randrange(0, 2):
            return self.get_file()
        else:
            return self.get_folder()

    def remove_path(self, path):
        try:
            self.files.remove(path)
        except ValueError:
            self.folders.remove(path)

    def replace_path(self, old_path, new_path):
        try:
            self.files.remove(old_path)
            self.files.append(new_path)
        except ValueError:
            self.folders.remove(old_path)
            self.folders.append(new_path)

    def get_new_path(self):
        return ("%s/%s" % (self.get_folder(), generate_name())).replace("//", "/")


class SkipCommand(Exception):
    pass


async def fuzzer(id, core, fs_state):
    while True:
        try:
            await _fuzzer_cmd(id, core, fs_state)
        except SkipCommand:
            fs_state.add_stat(id, "skipped command")


async def _fuzzer_cmd(id, core, fs_state):
    x = randrange(0, 100)
    await trio.sleep(x * 0.01)

    if x < 10:
        try:
            await core.fs.stat(fs_state.get_path())
            fs_state.add_stat(id, "stat_ok")
        except FSInvalidPath:
            fs_state.add_stat(id, "stat_bad")

    elif x < 20:
        path = fs_state.get_new_path()
        try:
            await core.fs.file_create(path)
            fs_state.files.append(path)
            fs_state.add_stat(id, "file_create_ok")
        except FSInvalidPath:
            fs_state.add_stat(id, "file_create_bad")

    elif x < 30:
        path = fs_state.get_file()
        size = randrange(0, 2000)
        try:
            await core.fs.file_read(path, size=size)
            fs_state.add_stat(id, "file_read_ok")
        except FSInvalidPath:
            fs_state.add_stat(id, "file_read_bad")

    elif x < 40:
        path = fs_state.get_file()
        buffer = b"x" * randrange(1, 1000)
        offset = randrange(0, 100)
        try:
            await core.fs.file_write(path, buffer, offset=offset)
            fs_state.add_stat(id, "file_write_ok")
        except FSInvalidPath:
            fs_state.add_stat(id, "file_write_bad")

    elif x < 50:
        path = fs_state.get_file()
        length = randrange(0, 100)
        try:
            await core.fs.file_truncate(path, length)
            fs_state.add_stat(id, "file_truncate_ok")
        except FSInvalidPath as exc:
            fs_state.add_stat(id, "file_truncate_bad")

    elif x < 60:
        path = fs_state.get_new_path()
        try:
            await core.fs.folder_create(path)
            fs_state.folders.append(path)
            fs_state.add_stat(id, "folder_create_ok")
        except FSInvalidPath:
            fs_state.add_stat(id, "folder_create_bad")

    elif x < 70:
        old_path = fs_state.get_path()
        if old_path == "/":
            # Happens too often otherwise
            raise SkipCommand()
        new_path = fs_state.get_new_path()
        try:
            await core.fs.move(old_path, new_path)
            fs_state.replace_path(old_path, new_path)
            fs_state.add_stat(id, "move_ok")
        except FSInvalidPath as exc:
            fs_state.add_stat(id, "move_bad")

    elif x < 80:
        path = fs_state.get_path()
        try:
            await core.fs.delete(path)
            fs_state.remove_path(path)
            fs_state.add_stat(id, "delete_ok")
        except FSInvalidPath:
            fs_state.add_stat(id, "delete_bad")

    elif x < 90:
        path = fs_state.get_file()
        try:
            await core.fs.file_flush(path)
            fs_state.add_stat(id, "flush_ok")
        except FSInvalidPath:
            fs_state.add_stat(id, "flush_bad")

    else:
        path = fs_state.get_path()
        try:
            await core.fs.sync(path)
            fs_state.add_stat(id, "sync_ok")
        except FSInvalidPath:
            fs_state.add_stat(id, "sync_bad")


@pytest.mark.trio
async def test_fuzz_core(request, running_backend, core, alice):
    await core.login(alice)
    async with trio.open_nursery() as nursery:
        fs_state = FSState()
        for i in range(FUZZ_PARALLELISM):
            nursery.start_soon(fuzzer, i, core, fs_state)
        await trio.sleep(FUZZ_TIME)
        nursery.cancel_scope.cancel()
    print("Stats:")
    for k, v in fs_state.get_cooked_stats():
        print(" - %s: %s%%" % (k, v))
