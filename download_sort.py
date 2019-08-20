import asyncio
import sys
from pathlib import Path

import aiofiles.os as asyncos

home = Path.home()
downloadDir = Path(home, "Downloads/")
documenttype = ("pdf", "pages", "numbers", "keynote", "xlsx", "xls", "doc", "docx", "ppt", "pptx", "odt", "odp",
                "txt", "html", "md", "rtf", "conf", "json", "csv")
picturetype = ("gif", "tiff", "jpg", "jpeg", "png", "xcf")
programtype = ("iso", "dmg", "app", "exe", "py", "jar", "swf", "apk")
archivetype = ("zip", "7z", "rar", "gz", "tar", "xz", "webarchive")
videotype = ("mp4", "m4v", "mov", "mkv", "flv")
audiotype = ("aac", "mp3", "aax", "m4a", "m4b", "wma", "flac", "wav")


async def makedir(directory: Path, name: str):
    newpath = Path(directory, name)
    if not newpath.exists():
        asyncos.mkdir(newpath)
    return newpath


async def all_files(path: Path) -> [Path]:
    files = []
    for item in path.iterdir():
        if not item.name.startswith('.'):
            if item.is_file():
                files.append(item)
            elif item.is_dir():
                subfiles = await all_files(item)
                files += subfiles
    return files


async def splitup(files: [Path]):
    documents = []
    pictures = []
    programs = []
    archives = []
    videos = []
    audios = []
    for file in files:
        ext = file.suffix.strip('.')
        if ext in documenttype:
            documents.append(file)
        elif ext in picturetype:
            pictures.append(file)
        elif ext in programtype:
            programs.append(file)
        elif ext in archivetype:
            archives.append(file)
        elif ext in videotype:
            videos.append(file)
        elif ext in audiotype:
            audios.append(file)
    return documents, pictures, programs, archives, videos, audios


async def movefile(file: Path, dest: Path):
    if file.parent != dest:
        dest = Path(dest, file.name)
        try:
            await asyncos.rename(file, dest)
        except FileExistsError:
            pass


async def sort(dir: Path):
    files = await all_files(dir)
    docs, pics, progs, archs, vids, auds = await splitup(files)
    if docs:
        docdir = await makedir(dir, "Dokumente")
        for doc in docs:
            await movefile(doc, docdir)
    if pics:
        picdir = await makedir(dir, "Bilder")
        for pic in pics:
            await movefile(pic, picdir)
    if progs:
        progdir = await makedir(dir, "Programme")
        for prog in progs:
            await movefile(prog, progdir)
    if archs:
        archdir = await makedir(dir, "Archive")
        for arch in archs:
            await movefile(arch, archdir)
    if vids:
        viddir = await makedir(dir, "Videos")
        for vid in vids:
            await movefile(vid, viddir)
    if auds:
        auddir = await makedir(dir, "Audios")
        for aud in auds:
            await movefile(aud, auddir)


async def cleanup(directory: Path):
    for item in directory.iterdir():
        if item.is_dir():
            await cleanup(item)
            try:
                item.rmdir()
            except OSError:
                pass


async def main(directory=downloadDir):
    directory = Path(directory)
    await sort(directory)
    await cleanup(directory)


def display_results():
    GUI.getPopup("Finished sorting the given Folder.")


if __name__ == "__main__":
    if len(sys.argv) == 1:
        import GUI

        event, values = GUI.getFolderInputWindow(initial_folder=str(downloadDir.absolute()))
        if event == "OK" and values[0] != "":
            asyncio.run(main(values[0]))
            display_results()
        elif event == "OK":
            asyncio.run(main())
            display_results()
        else:
            GUI.getErrorWindow("You must provide a folder to sort")
            sys.exit(1)
    elif len(sys.argv) == 2:
        asyncio.run(main(sys.argv[1]))
    else:
        print("Usage: download_sort.py DIRECTORY_TO_SORT")
        sys.exit(1)
