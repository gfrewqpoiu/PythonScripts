import asyncio
import decimal
import json
import nest_asyncio  # type: ignore
from abc import ABC, abstractmethod
from pathlib import *
from asyncrun import asyncrun
from typing import Union, Tuple, List, Dict, Optional, Any

rclone_flags = '--fast-list'

loop: asyncio.AbstractEventLoop


def decode(input: str) -> Any:
    return json.loads(input)


def split(list: list) -> Tuple[list, list]:
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
        self.drive = drive  # type: str
        self.path = PurePosixPath(path, item['Path'])
        if not drive.endswith(':'):
            drive += ':'
        self.fullpath = PurePosixPath(drive, self.path)
        self.name: str = item['Name']
        self.parent: Optional[PurePosixPath] = self.path.parent
        self.is_directory: bool = False
        self._size: int

    def __str__(self):
        return self.name

    @abstractmethod
    async def get_size(self) -> int:
        raise NotImplementedError

    async def get_size_str(self) -> str:
        size = decimal.Decimal(await self.get_size())
        if size > 1024:
            size = size / 1024  # KB
            if size > 1024:
                size = size / 1024  # MB
                if size > 1024:
                    size = size / 1024  # GB
                    if size > 1024:
                        size = size / 1024  # TB
                        if size > 1024:
                            size = size / 1024  # PB
                            return str(round(float(size), 3)) + " PBytes"
                        else:
                            return str(round(float(size), 3)) + " TBytes"
                    else:
                        return str(round(float(size), 3)) + " GBytes"
                else:
                    return str(round(float(size), 3)) + " MBytes"

            else:
                return str(round(float(size), 3)) + " KBytes"

        else:
            return str(size) + " Bytes"


class RcloneFile(RcloneItem):
    """Represents a file on a Rclone Drive"""

    def __init__(self, item, drive, path):
        super().__init__(item, drive, path)
        self.filetype: str = item['MimeType']
        self.purename = self.path.stem
        self.extension = self.path.suffix
        if int(item["Size"]) > 0:
            self._size = int(item['Size'])
        else:
            self._size = 0
        self._hash: str

    async def get_size(self) -> int:
        return self._size

    async def get_hash(self) -> str:
        if self._hash is None:
            hash = await fetch_hash(self.fullpath)
            self._hash = hash.split()[0]
        return self._hash

    async def equals(self, other):
        """Checks if the given Files are equal."""
        if not isinstance(other, RcloneFile):
            return False
        hash1 = await self.get_hash()
        hash2 = await other.get_hash()
        if (hash1 == hash2) and (await self.get_size() == await other.get_size()):
            return True
        else:
            return False

    def __eq__(self, other) -> bool:
        """This only works properly when the files have their hashes pre-filled by calling the coroutine get_hash."""
        if not isinstance(other, RcloneFile):
            return False

        if self._hash is None or other._hash is None:
            if self._hash is None:
                loop.run_until_complete(self.get_hash())
            if other._hash is None:
                loop.run_until_complete(other.get_hash())

            print("This has blockingly called get_hash since one of these didn't have a hash specified."
                  "Consider using the equals coroutine instead.")

        if (self._hash == other._hash) and (self._size == other._size):
            return True
        else:
            return False


class RcloneDirectory(RcloneItem):
    """Represents a folder on a rclone Drive"""

    def __init__(self, item, drive, path):
        super().__init__(item, drive, path)
        self.is_directory: bool = True
        self.populated: bool = False
        self._contents: List[RcloneItem] = []
        self._amount = -1

    async def populate(self):
        self._contents = await ls(self.drive, self.path)
        self.populated = True

    async def get_contents(self, recursive: bool = False) -> List[RcloneItem]:
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

    async def find(self, search: str):
        search = search.lower()
        for item in await self.get_contents():
            if search in item.name.lower():
                return item
        return None


async def ls(drive: str, directory: Union[str, PurePosixPath], recursive_flat: bool = False) -> List[RcloneItem]:
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
    results: List[RcloneItem] = []
    for item in result:
        if not item['IsDir']:
            results.append(RcloneFile(item, drive, directory))
        else:
            new_directory = RcloneDirectory(item, drive, directory)
            results.append(new_directory)

    return results


async def tree(drive: str = "Drive", directory: Union[str, PurePosixPath] = "") -> RcloneDirectory:
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
        root.parent = None
    fulltree: List[RcloneItem] = await flatls(drive, directory)
    fulltree.append(root)
    for file in fulltree:
        if isinstance(file, RcloneDirectory):
            await fill_path(file, fulltree)
    return root


async def flatls(drive: str, directory: Union[str, PurePosixPath]) -> List[RcloneItem]:
    return await ls(drive, directory, recursive_flat=True)


async def size(full_path: Union[str, PurePosixPath]) -> Tuple[int, int]:
    result = await asyncrun('rclone', 'size', full_path, '--json', rclone_flags)
    results = decode(result)
    amount = int(results['count'])
    totalsize = int(results['bytes'])
    return amount, totalsize


async def fetch_hash(full_path: Union[str, PurePosixPath]) -> str:
    res = await asyncrun('rclone', 'md5sum', full_path, rclone_flags)
    return res


async def copy(src_full_path: Union[str, PurePath], dest_full_path: Union[str, PurePath]):
    await asyncrun('rclone', 'copy', src_full_path, dest_full_path, '-c', rclone_flags)


async def move(src_full_path: Union[str, PurePath], dest_full_path: Union[str, PurePath]):
    await asyncrun('rclone', 'move', src_full_path, dest_full_path, '-c', rclone_flags)


async def delete_file(full_path: Union[str, PurePosixPath]):
    await asyncrun('rclone', 'deletefile', full_path, rclone_flags, '--drive-use-trash=true')


async def sync(src_full_path: Union[str, PurePath], dest_full_path: Union[str, PurePath], *args):
    await asyncrun('rclone', 'sync', src_full_path, dest_full_path, '-c', rclone_flags, *args)


async def main():
    global loop
    import GUI
    loop = asyncio.get_running_loop()
    nest_asyncio.apply()
    event, values = GUI.rclonewindow()
    if event == 'OK':
        drive = values[0]
        path = values[1]
        contents = await ls(drive, path)
        GUI.rcloneoutputwindow(contents)


if __name__ == '__main__':
    asyncio.run(main())
