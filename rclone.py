import asyncio
import decimal
import json
import os.path
import shlex
from os.path import splitext

from asyncrun import asyncrun

rclone_flags = '--fast-list'


def decode(input):
    if input is None:
        return
    return json.loads(input)


def split(list):
    files = []
    folders = []
    for item in list:
        if item["IsDir"]:
            folders.append(item)
        else:
            files.append(item)
    return files, folders


def filetype(item):
    return item['MimeType']


class RcloneItem():
    def __init__(self, item, drive, path, parent=None):
        self.drive = drive
        self.path = path + item['Path']
        self.fullpath = drive + ':' + self.path
        self.name = item['Name']
        if parent is None:
            self.parent = self.path.replace(self.name, "")
            if self.parent.endswith("//"):
                self.parent.replace("//", "/")
        else:
            self.parent = parent
        self.is_directory = False
        self._size = None
        self._hash = None

    def __str__(self):
        return self.name

    async def get_size(self):
        pass

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
    def __init__(self, item, drive, path, parent=None):
        super().__init__(item, drive, path, parent)
        self.filetype = item['MimeType']
        self.purename, self.extension = splitext(self.path)
        if int(item["Size"]) > 0:
            self._size = item['Size']
        else:
            self._size = 0

    async def get_size(self):
        return self._size

    def get_hash(self):
        if self._hash == None:
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
    def __init__(self, item, drive, path, parent=None):
        super().__init__(item, drive, path, parent)
        self.is_directory = True
        if not self.path.endswith("/"):
            self.path += "/"
        self.populated = False
        self._contents = []

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


async def ls(drive, directory="", recursive_flat=False) -> [RcloneItem]:
    if not directory.endswith('/'):
        directory = directory + '/'
    src = drive + ":" + directory
    if recursive_flat:
        res = await asyncrun('rclone', 'lsjson', src, rclone_flags, "-R")
    else:
        res = await asyncrun('rclone', 'lsjson', src, rclone_flags)
    result = decode(res)
    results = []
    for item in result:
        if not item['IsDir']:
            results.append(RcloneFile(item, drive, directory))
        else:
            dir = RcloneDirectory(item, drive, directory)
            results.append(dir)

    return results


async def tree(drive, directory) -> RcloneDirectory:
    def fill_path(path: RcloneDirectory, list: list):
        for item in list:
            if item.parent == path.path:
                path._contents.append(item)

        path.populated = True

    directory = shlex.quote(directory)
    name = os.path.dirname(directory)
    item = {'Path': directory, 'Name': os.path.basename(name), 'IsDir': True}
    root = RcloneDirectory(item, drive, "")
    fulltree = await flatls(drive, directory)
    tree = []
    tree.append(root)
    fulltree.append(root)
    for item in fulltree:
        if isinstance(item, RcloneDirectory):
            fill_path(item, fulltree)
    return tree[0]


async def flatls(drive, directory) -> [RcloneItem]:
    return await ls(drive, directory, recursive_flat=True)

async def size(full_path: str):
    full_path = full_path.replace(" ", "\ ")
    result = await asyncrun('rclone', 'size', full_path, '--json', rclone_flags)
    results = decode(result)
    amount = results['count']
    size = results['bytes']
    return amount, size


async def fetch_hash(full_path: str):
    full_path = full_path.replace(" ", "\ ")
    res = await asyncrun('rclone', 'md5sum', full_path, rclone_flags)
    return res


async def copy(src_full_path: str, dest_full_path: str):
    await asyncrun('rclone', 'copy', src_full_path, dest_full_path, '-c', rclone_flags)

async def move(src_full_path: str, dest_full_path: str):
    await asyncrun('rclone', 'move', src_full_path, dest_full_path, '-c', rclone_flags)


async def delete_file(full_path):
    await asyncrun('rclone', 'deletefile', full_path, rclone_flags, '--drive-use-trash=true')

async def main():
    tree = await(ls('Drive', ''))
    print("Files:")
    for item in tree:
        if isinstance(item, RcloneFile):
            print(item.name)
            print(await item.get_size_str())
    print("Folders:")
    for item in tree:
        if isinstance(item, RcloneDirectory):
            print(item.name)
            if item.name == "Canary Mail":
                print(await item.get_amount())

if __name__ == '__main__':
    asyncio.run(main())
