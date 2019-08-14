import asyncio.queues
import os
import shutil

import rclone
import video_convert

temppath = os.getcwd() + "/tmp/"
basepath = "Videos/"
queue = []


async def download(file: rclone.RcloneFile):
    await rclone.copy(file.fullpath, temppath)
    return temppath + file.name


async def get_path_content(drive, path):
    content = await rclone.ls(drive, path)
    return content


async def get_folder_content(folder: rclone.RcloneDirectory):
    content = await folder.get_contents()
    return content


async def get_videos_to_convert(folder: rclone.RcloneDirectory):
    queue = []
    content = await get_folder_content(folder)
    for item in content:
        if isinstance(item, rclone.RcloneFile):
            type = str(item.filetype)
            if type.startswith('video'):
                if type != 'video/mp4':
                    queue.append(item)
    return queue


async def upload(file, dest):
    await rclone.copy(file, dest)


async def convert(filepath):
    newfilepath, oldext = os.path.splitext(filepath)
    await video_convert.convert(filepath, newfilepath + '.mp4')
    return newfilepath


async def cleanup(path=temppath):
    shutil.rmtree(path)

async def main(drive, path=basepath):
    content = await get_path_content(drive, path)
    for item in content:
        to_convert = await get_videos_to_convert(item)
        for item in to_convert:
            print("Starting Download of: " + item.name)
            filepath = await download(item)
            print("Downloaded: " + item.name)
            newfilepath = await convert(filepath)
            print("Converted it")
            newcloudpath = item.drive + ':' + item.purename + '.mp4'
            await upload(newfilepath, newcloudpath)
            print("Uploaded it")
            await cleanup()


if __name__ == '__main__':
    asyncio.run(main('Drive'))