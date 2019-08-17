import asyncio.queues
import logging
import os

import aiofiles.os as asyncos

import rclone
import video_convert

temppath = os.getcwd() + "/tmp/"
basepath = "Videos/"

logging.basicConfig(level=logging.INFO)


class Job():
    _temppath = temppath
    newext = ".mp4"
    log = logging.getLogger()

    def __init__(self, inputfile: rclone.RcloneFile):
        self.is_downloaded = False
        self.is_converted = False
        self.is_uploaded = False
        self.inputfile = inputfile
        self.path = self._temppath + self.inputfile.name
        self.newfilepath, self.oldext = os.path.splitext(self.path)
        self.newfilepath += self.newext
        self.parentpath = self.inputfile.fullpath.replace(self.inputfile.name, "")
        self.newname, self.oldext = os.path.splitext(self.inputfile.name)
        self.newname += self.newext
        self.log.debug("New Job created with:")
        self.log.debug("Inputtfile: " + inputfile.path)

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
        if self.oldext not in ['.mkv', '.mov']:
            await rclone.delete_file(self.inputfile.fullpath)

    async def run(self):
        await self.download()
        await self.convert()
        await self.upload()
        await self.cleanup()


async def get_path_content(drive, path):
    content = await rclone.ls(drive, path)
    return content


async def get_folder_content(folder: rclone.RcloneDirectory):
    content = await folder.get_contents()
    return content


async def get_videos_to_convert(folder: rclone.RcloneItem):
    queue = []

    def checkfile(file):
        type = str(file.filetype)  # Finally
        if type.startswith('video'):
            if type != 'video/mp4':
                queue.append(file)

    if isinstance(folder, rclone.RcloneFile):
        checkfile(folder)
    return queue


async def check_already_converted(file: rclone.RcloneFile):
    parentfolder = file.parent
    parentfolder = await rclone.ls(file.drive, parentfolder)
    for item in parentfolder.get_content():
        if file.purename + '.mp4' == item.name:
            return False
    return True


async def checkfile(file: rclone.RcloneFile):
    type = str(file.filetype)  # Finally
    if type.startswith('video'):
        if type != 'video/mp4':
            if not await check_already_converted(file):
                return True
        else:
            return False


async def worker(queue: asyncio.Queue):
    while True:
        job = await queue.get()
        await job.run()
        queue.task_done()


async def main(drive, path=basepath):
    queue = asyncio.Queue(maxsize=3)
    log = logging.getLogger()
    content = await rclone.flatls(drive, path)
    task = asyncio.create_task(worker(queue))
    for item in content:
        if isinstance(item, rclone.RcloneFile):
            if await checkfile(item):
                job = Job(inputfile=item)
                await queue.put(job)

    await queue.join()
    task.cancel()
    log.info("Done with all the conversions!")


if __name__ == '__main__':
    asyncio.run(main('Drive'))