import asyncio
import decimal
import json
from abc import ABC
from pathlib import *
from asyncrun import asyncrun
from typing import Union

rclone_flags = '--fast-list'


def decode(input: str):
    if input is None:
        return
    return json.loads(input)


def split(list: list):
    files = []
    folders = []
    for item in list:
        if item["IsDir"]:
            folders.append(item)
        else:
            files.append(item)
    return files, folders


class RcloneItem(ABC):
    """Represents the concept of an object on a rclone Drive.
    Both files and folders."""

    def __init__(self, item, drive: str, path):
        self.drive = drive
        self.path = PurePosixPath(path, item['Path'])
        if not drive.endswith(':'):
            drive += ':'
        self.fullpath = PurePosixPath(drive, self.path)
        self.name = item['Name']
        self.parent = self.path.parent
        self.is_directory = False
        self._size = None
        self._hash = None

    def __str__(self):
        return self.name

    async def get_size(self):
        raise NotImplementedError

    async def get_size_str(self):
        size = decimal.Decimal(await self.get_size())
        if size > 1024:
            size = size / 1024 #KB
            if size > 1024:
                size = size / 1024 #MB
                if size > 1024:
                    size = size / 1024 #GB
                    if size > 1024:
                        size = size / 1024 #TB
                        if size > 1024:
                            size = size / 1024 #PB
                            return str(round(size, 3)) + " PBytes"
                        else:
                            return str(round(size, 3)) + " TBytes"
                    else:
                        return str(round(size, 3)) + " GBytes"
                else:
                    return str(round(size, 3))+ " MBytes"

            else:
                return str(round(size, 3)) + " KBytes"

        else:
            return str(size) + " Bytes"


class RcloneFile(RcloneItem):
    """Represents a file on a Rclone Drive"""

    def __init__(self, item, drive, path):
        super().__init__(item, drive, path)
        self.filetype = item['MimeType']
        self.purename = self.path.stem
        self.extension = self.path.suffix
        if int(item["Size"]) > 0:
            self._size = item['Size']
        else:
            self._size = 0

    async def get_size(self):
        return self._size

    def get_hash(self):
        if self._hash is None:
            self._hash = fetch_hash(self.fullpath)
        return self._hash

    def __eq__(self, other):
        if not isinstance(other, RcloneFile):
            return False
        hash1 = self.get_hash()
        hash2 = other.get_hash()
        if (hash1 == hash2) and (self.get_size() == other.get_size()):
            return True
        else:
            return False


class RcloneDirectory(RcloneItem):
    """Represents a folder on a rclone Drive"""

    def __init__(self, item, drive, path):
        super().__init__(item, drive, path)
        self.is_directory = True
        self.populated = False
        self._contents = []
        self._amount = -1

    async def populate(self):
        self._contents = await ls(self.drive, self.path)
        self.populated = True

    async def get_contents(self, recursive = False):
        if not self.populated:
            await self.populate()
        if recursive:
            for item in self._contents:
                if isinstance(item, RcloneDirectory):
                    await item.get_contents(True)
        return self._contents

    async def get_size(self):
        if self._size is None:
            self._amount, self._size = await size(self.fullpath)
        if self._size < 0:
            self._size = 0
        return self._size

    async def get_amount(self):
        if self._size is None:
            await self.get_size()
        return self._amount


async def ls(drive: str, directory: Union[str, PurePosixPath], recursive_flat: bool = False) -> [RcloneItem]:
    if not isinstance(directory, PurePosixPath):
        directory = PurePosixPath(directory)
    if not drive.endswith(':'):
        drive += ':'
    src = PurePosixPath(drive, directory)
    if recursive_flat:
        res = await asyncrun('rclone', 'lsjson', str(src), rclone_flags, "-R")
    else:
        res = await asyncrun('rclone', 'lsjson', str(src), rclone_flags)
    result = decode(res)
    results = []
    for item in result:
        if not item['IsDir']:
            results.append(RcloneFile(item, drive, directory))
        else:
            new_directory = RcloneDirectory(item, drive, directory)
            results.append(new_directory)

    return results


async def tree(drive: str, directory: Union[str, PurePosixPath]) -> RcloneDirectory:
    if not isinstance(directory, PurePosixPath):
        directory = PurePosixPath(directory)

    async def fill_path(path: RcloneDirectory, items: list):
        for item in items:
            if item.parent == path.path:
                path._contents.append(item)

        path.populated = True

    item = {'Path': directory, 'Name': directory.name, 'IsDir': True}
    root = RcloneDirectory(item, drive, "")
    if directory == "":
        root.parent = "{ROOTDIR}"
    fulltree = await flatls(drive, directory)
    fulltree.append(root)
    for item in fulltree:
        if isinstance(item, RcloneDirectory):
            await fill_path(item, fulltree)
    return root


async def flatls(drive: str, directory: Union[str, PurePosixPath]) -> [RcloneItem]:
    return await ls(drive, directory, recursive_flat=True)


async def size(full_path: Union[str, PurePosixPath]):
    result = await asyncrun('rclone', 'size', full_path, '--json', rclone_flags)
    results = decode(result)
    amount = results['count']
    size = results['bytes']
    return amount, size


async def fetch_hash(full_path: str or PurePosixPath):
    if not isinstance(full_path, str):
        full_path = str(full_path)
    res = await asyncrun('rclone', 'md5sum', full_path, rclone_flags)
    return res


async def copy(src_full_path: PurePosixPath, dest_full_path: PurePosixPath):
    if (not isinstance(src_full_path, str)) or (not isinstance(dest_full_path, str)):
        src_full_path = str(src_full_path)
        dest_full_path = str(dest_full_path)
    await asyncrun('rclone', 'copy', src_full_path, dest_full_path, '-c', rclone_flags)


async def move(src_full_path: str or PurePosixPath, dest_full_path: str or PurePosixPath):
    if (not isinstance(src_full_path, str)) or (not isinstance(dest_full_path, str)):
        src_full_path = str(src_full_path)
        dest_full_path = str(dest_full_path)
    await asyncrun('rclone', 'move', src_full_path, dest_full_path, '-c', rclone_flags)


async def delete_file(full_path: str or PurePosixPath):
    await asyncrun('rclone', 'deletefile', full_path, rclone_flags, '--drive-use-trash=true')


async def sync(src_full_path: str or PurePosixPath, dest_full_path: str or PurePosixPath, *args):
    await asyncrun('rclone', 'sync', src_full_path, dest_full_path, '-c', rclone_flags, *args)


async def main():
    import GUI
    event, values = GUI.rclonewindow()
    if event == 'OK':
        drive = values[0]
        path = values[1]
        contents = await ls(drive, path)
        GUI.rcloneoutputwindow(contents)


if __name__ == '__main__':
    asyncio.run(main())
