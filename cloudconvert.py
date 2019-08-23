import asyncio.queues
import logging
import pickle
import pickletools
import pprint
from pathlib import *

import aiofiles.os as asyncos

import rclone
import video_convert

temppath = Path(Path.cwd(), 'tmp')
basepath = PurePosixPath("Videos/")
print = pprint.pprint
logging.basicConfig(level=logging.INFO)
queue = asyncio.Queue()

class Job():
    _temppath = temppath
    newext = ".mp4"
    log = logging.getLogger()

    def __init__(self, inputfile: rclone.RcloneFile):
        self.is_downloaded = False
        self.is_converted = False
        self.is_uploaded = False
        self.inputfile = inputfile
        self.path = Path(self._temppath, self.inputfile.name)
        self.newfilepath = self.path.with_suffix('.mp4')
        self.parentpath = self.inputfile.fullpath.parent
        self.newname = self.inputfile.purename
        self.newname += '.mp4'
        self.log.debug("New Job created with:")
        self.log.debug("Inputtfile: " + str(inputfile.path))

    async def download(self):
        await rclone.copy(self.inputfile.fullpath, self._temppath)
        self.is_downloaded = True
        self.log.info("Downloaded file: " + self.inputfile.name)

    async def convert(self):
        if not self.is_downloaded:
            raise FileNotFoundError
        self.log.debug("Started conversion of: " + self.inputfile.name)
        await video_convert.convert(self.path, self.newfilepath)
        self.log.info("Finished conversion of: " + self.newname)
        self.is_converted = True

    async def upload(self):
        self.log.debug("Starting upload of: " + self.newname)
        await rclone.copy(self.newfilepath, self.parentpath)
        self.log.info("Finished upload of: " + self.newname)

    async def cleanup(self):
        await asyncos.remove(self.path)
        await asyncos.remove(self.newfilepath)
        # if self.oldext not in ['.mkv', '.mov']:
        # await rclone.delete_file(self.inputfile.fullpath)

    async def run(self):
        await self.download()
        await self.convert()
        await self.upload()
        await self.cleanup()

    def __str__(self):
        return f"{self.inputfile.purename}: Downloaded: {self.is_downloaded}, Converted: {self.is_converted}, Uploaded: {self.is_uploaded}"


async def get_path_content(drive, path) -> [rclone.RcloneItem]:
    content = await rclone.ls(drive, path)
    return content


async def get_folder_content(folder: rclone.RcloneDirectory) -> [rclone.RcloneItem]:
    content = await folder.get_contents()
    return content


async def check_already_converted(file: rclone.RcloneFile, contents: [rclone.RcloneItem]) -> bool:
    """Checks whether the given file is already converted in the given contents
    :param file The file to check
    :param contents A list of contents.
    :returns True or false"""
    filename = file.purename
    for item in contents:
        if filename + '.mp4' == item.name:
            return True
    return False


async def check_to_convert(file: rclone.RcloneFile, contents: [rclone.RcloneItem]) -> bool:
    """Checks if the given file needs to be converted."""
    filetype = str(file.filetype)  # Finally
    if filetype.startswith('video'):
        if (type != 'video/mp4') and (file.extension not in [".mp4", ".m4v"]):
            already_there = await check_already_converted(file, contents)
            if not already_there:
                return True
    else:
        return False


async def worker(queue: asyncio.Queue):
    log = logging.getLogger()
    while True:
        job = await queue.get()
        await job.run()
        log.info(f"{queue.qsize()} items left to do")
        queue.task_done()


async def send_jobs(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    global queue
    addr = writer.get_extra_info('peername')
    print(f"Got connection from {addr}")
    pickledqueue = pickletools.optimize(pickle.dumps(queue._queue, protocol=4))
    writer.write(pickledqueue)
    await writer.drain()
    writer.close()


async def main(drive, path=basepath):
    global queue
    async def search(folder: rclone.RcloneDirectory):
        global queue
        contents = await folder.get_contents()
        for item in contents:
            if isinstance(item, rclone.RcloneDirectory):
                await search(item)
            elif isinstance(item, rclone.RcloneFile):
                to_convert = await check_to_convert(item, contents)
                if to_convert:
                    job = Job(inputfile=item)
                    await queue.put(job)

    log = logging.getLogger()
    server = await asyncio.start_server(send_jobs, '0.0.0.0', 8888, start_serving=True)
    print("Now accepting connections!")
    root = await rclone.tree(drive, path)
    task = asyncio.create_task(worker(queue))
    await search(root)
    log.info(f"Found {queue.qsize()} items to convert")
    await queue.join()
    await server.close()
    task.cancel()
    log.info("Done with all the conversions!")


if __name__ == '__main__':
    asyncio.run(main('Drive'))
