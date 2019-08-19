import asyncio
import os
import sys
from pathlib import Path

import aiofiles.os as asyncos

home = os.fsdecode(Path.home())
downloadDir = home + "/Downloads/"
documenttype = ("pdf", "pages", "numbers", "keynote", "xlsx", "xls", "doc", "docx", "ppt", "pptx", "odt", "odp",
                "txt", "html", "md", "rtf", "conf", "json", "csv")
picturetype = ("gif", "tiff", "jpg", "jpeg", "png")
programtype = ("iso", "dmg", "app", "exe", "py", "jar", "swf")
archivetype = ("zip", "7z", "rar", "gz", "tar", "xz", "webarchive")
videotype = ("mp4", "m4v", "mov", "mkv", "flv")
audiotype = ("aac", "mp3", "aax", "m4a", "m4b", "wma", "flac", "wav")


async def makedir(dir, name: str):
    try:
        os.mkdir(os.fsdecode(dir) + name)
    except FileExistsError:
        pass


async def all_files(path):
    files = []
    with os.scandir(path) as it:
        for item in it:
            if not item.name.startswith('.'):
                if item.is_file():
                    files.append(item)
                elif item.is_dir():
                    subfiles = await all_files(item)
                    for subfile in subfiles:
                        files.append(subfile)
    return files


async def splitup(files):
    documents = []
    pictures = []
    programs = []
    archives = []
    videos = []
    audios = []
    for file in files:
        name = file.name.lower()
        if name.endswith(documenttype):
            documents.append(file)
        elif name.endswith(picturetype):
            pictures.append(file)
        elif name.endswith(programtype):
            programs.append(file)
        elif name.endswith(archivetype):
            archives.append(file)
        elif name.endswith(videotype):
            videos.append(file)
        elif name.endswith(audiotype):
            audios.append(file)
    return documents, pictures, programs, archives, videos, audios


async def movefile(file, dest):
    try:
        await asyncos.rename(file, dest)
    except FileExistsError:
        pass


async def maybemovefile(file, dest):
    if not os.fsdecode(file).startswith(dest):
        await movefile(file, dest + file.name)


async def sort(dir):
    files = await all_files(dir)
    docs, pics, progs, archs, vids, auds = await splitup(files)
    if docs:
        await makedir(dir, "Dokumente")
        docdir = os.fsdecode(dir) + "Dokumente/"
        for doc in docs:
            await maybemovefile(doc, docdir)
    if pics:
        await makedir(dir, "Bilder")
        picdir = os.fsdecode(dir) + "Bilder/"
        for pic in pics:
            await maybemovefile(pic, picdir)
    if progs:
        await makedir(dir, "Programme")
        progdir = os.fsdecode(dir) + "Programme/"
        for prog in progs:
            await maybemovefile(prog, progdir)
    if archs:
        await makedir(dir, "Archive")
        archdir = os.fsdecode(dir) + "Archive/"
        for arch in archs:
            await maybemovefile(arch, archdir)
    if vids:
        await makedir(dir, "Videos")
        viddir = os.fsdecode(dir) + "Videos/"
        for vid in vids:
            await maybemovefile(vid, viddir)
    if auds:
        await makedir(dir, "Audios")
        auddir = os.fsdecode(dir) + "Audios/"
        for aud in auds:
            await maybemovefile(aud, auddir)


async def main(dir=downloadDir):
    if not dir.endswith("/"):
        dir += "/"
    await sort(dir)


if __name__ == "__main__":
    if len(sys.argv) == 1:
        import GUI

        event, values = GUI.getFolderInputWindow(initial_folder=downloadDir)
        if event == "OK" and values[0] != "":
            asyncio.run(main(values[0]))
        elif event == "OK":
            asyncio.run(main())
        else:
            GUI.getErrorWindow("You must provide a folder to sort")
            sys.exit(1)
    elif len(sys.argv) == 2:
        asyncio.run(main(sys.argv[1]))
    else:
        print("Usage: download_sort.py DIRECTORY_TO_SORT")
