import rclone
from asyncrun import asyncrun
from video_convert import convert
import os
import asyncio.queues

temppath = os.getcwd() + "/tmp/"
basepath = "Videos/"
queue = []

async def download(file):
    await rclone.copy(file, temppath)


async def get_path_content(drive, path):
    content = await rclone.ls(drive, path)
    return content


async def get_folder_content(folder: rclone.RcloneDirectory):
    content = await folder.get_contents()
    return content


async def get_videos_to_convert(folder: rclone.RcloneDirectory):
    content = await get_folder_content(folder)
    for item in content:
        if isinstance(item, rclone.RcloneFile):
            type = str(item.filetype)
            if type.startswith('video'):
                if type != 'video/mp4':
                    queue.append(item)
    for item in queue:
        print(item.name)

async def main(drive, path=basepath):
    content = await get_path_content(drive, path)
    for item in content:
        await get_videos_to_convert(item)

if __name__ == '__main__':
    asyncio.run(main('Drive'))