import asyncio
import logging
import pickle
import pickletools
import pprint
import rclone
import video_convert
import aiofiles.os as asyncos  # type: ignore
from collections import deque
from pathlib import *
from typing import List, Union, NoReturn


temppath = Path(Path.cwd(), 'tmp')
basepath = PurePosixPath("Videos/")
print = pprint.pprint
logging.basicConfig(level=logging.INFO)
server: asyncio.AbstractServer
queue: asyncio.Queue
running_job: 'Job'


class Job:
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

    async def download(self) -> None:
        await rclone.copy(self.inputfile.fullpath, self._temppath)
        self.is_downloaded = True
        self.log.info("Downloaded file: " + self.inputfile.name)

    async def convert(self) -> None:
        if not self.is_downloaded:
            raise FileNotFoundError
        self.log.debug("Started conversion of: " + self.inputfile.name)
        await video_convert.convert(self.path, self.newfilepath)
        self.log.info("Finished conversion of: " + self.newname)
        self.is_converted = True

    async def upload(self) -> None:
        self.log.debug("Starting upload of: " + self.newname)
        await rclone.copy(self.newfilepath, self.parentpath)
        self.log.info("Finished upload of: " + self.newname)

    async def cleanup(self) -> None:
        await asyncos.remove(self.path)
        await asyncos.remove(self.newfilepath)
        # if self.oldext not in ['.mkv', '.mov']:
        # await rclone.delete_file(self.inputfile.fullpath)

    async def run(self) -> None:
        await self.download()
        await self.convert()
        await self.upload()
        await self.cleanup()

    def __str__(self) -> str:
        return f"{self.inputfile.purename}: Downloaded: {self.is_downloaded}, Converted: {self.is_converted}, Uploaded: {self.is_uploaded}"


async def get_path_content(drive, path) -> List[rclone.RcloneItem]:
    content = await rclone.ls(drive, path)
    return content


async def get_folder_content(folder: rclone.RcloneDirectory) -> List[rclone.RcloneItem]:
    content = await folder.get_contents()
    return content


async def check_already_converted(file: rclone.RcloneFile, contents: List[rclone.RcloneItem]) -> bool:
    """Checks whether the given file is already converted in the given contents
    :param file The file to check
    :param contents A list of contents.
    :returns True or false"""
    filename = file.purename
    for item in contents:
        if filename + '.mp4' == item.name:
            return True
    return False


async def check_to_convert(file: rclone.RcloneFile, contents: List[rclone.RcloneItem]) -> bool:
    """Checks if the given file needs to be converted."""
    filetype = str(file.filetype)  # Finally
    if filetype.startswith('video'):
        if (type != 'video/mp4') and (file.extension not in [".mp4", ".m4v"]):
            already_there = await check_already_converted(file, contents)
            if not already_there:
                return True
    return False


async def worker(queue: asyncio.Queue) -> NoReturn:
    global running_job
    log = logging.getLogger()
    while True:
        job = await queue.get()
        running_job = job
        await job.run()
        log.info(f"{queue.qsize()} items left to do")
        queue.task_done()


async def create_server(ip: str = '0.0.0.0', port: int = 8890) -> None:
    server = await asyncio.start_server(send_jobs, ip, port, start_serving=False)  # type: ignore
    print("Now accepting connections!")
    async with server:  # type: ignore
        await server.serve_forever()  # type: ignore


async def send_jobs(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
    global queue
    addr = writer.get_extra_info('peername')
    print(f"Got connection from {addr}")
    sendqueue = deque(queue._queue)  # type: ignore
    sendqueue.appendleft(running_job)
    pickledqueue = pickletools.optimize(pickle.dumps(sendqueue, protocol=4))
    writer.write(pickledqueue)
    await writer.drain()
    writer.close()


async def main(drive: str, path: Union[str, PurePosixPath] = basepath) -> None:
    loop = asyncio.get_event_loop()
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

    queue = asyncio.Queue(loop=loop)
    log = logging.getLogger()
    root = await rclone.tree(drive, path)
    task = asyncio.create_task(worker(queue))
    server = asyncio.create_task(create_server())
    await search(root)
    log.info(f"Found {queue.qsize()} items to convert")
    await queue.join()
    task.cancel()
    server.cancel()
    log.info("Done with all the conversions!")


if __name__ == '__main__':
    asyncio.run(main('Drive'))
