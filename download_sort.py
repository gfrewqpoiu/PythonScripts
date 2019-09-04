import asyncio
import sys
import GUI
from pathlib import Path
from typing import List, Union, Tuple

import aiofiles.os as asyncos  # type: ignore

home = Path.home()
downloadDir = Path(home, "Downloads/")
documenttype = ("pdf", "pages", "numbers", "keynote", "xlsx", "xls", "doc", "docx", "ppt", "pptx", "odt", "odp",
                "txt", "html", "md", "rtf", "conf", "json", "csv", "rtfd")
picturetype = ("gif", "tiff", "jpg", "jpeg", "png", "xcf")
programtype = ("iso", "dmg", "app", "exe", "py", "jar", "swf", "apk")
archivetype = ("zip", "7z", "rar", "gz", "tar", "xz", "webarchive")
videotype = ("mp4", "m4v", "mov", "mkv", "flv")
audiotype = ("aac", "mp3", "aax", "m4a", "m4b", "wma", "flac", "wav")


async def makedir(directory: Path, name: str) -> Path:
    newpath = Path(directory, name)
    if not newpath.exists():
        await asyncos.mkdir(newpath)
    return newpath


async def all_files(path: Path) -> List[Path]:
    files = []
    for item in path.iterdir():
        if not item.name.startswith('.'):
            if item.is_file():
                files.append(item)
            elif item.is_dir():
                subfiles = await all_files(item)
                files += subfiles
    return files


async def splitup(files: List[Path]) -> Tuple[List[Path], List[Path], List[Path], List[Path], List[Path], List[Path]]:
    """Splits the files based on the file extension.

    :param files: A list of Paths(Files) to split up.
    :returns A Tuple of Paths in the following order: Documents, Pictures, Programs, Archives, Videos, Audios"""
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


async def move_file(file: Path, dest: Path) -> None:
    """Moves the file from its path to the new destination.

    :param file: The file to move.
    :param dest: The folder to move the file to."""
    dest = dest.absolute()
    if file.parent != dest:
        destination = Path(dest, file.name)
        if not dest.exists():
            await asyncos.rename(file, destination)
        else:
            await move_existing_file(file, destination)


async def move_existing_file(file: Path, dest: Path, count: int = 1) -> None:
    desti = dest.absolute()
    destination = Path(desti.parent, desti.stem + '-' + str(count) + desti.suffix)
    if not destination.exists():
        await asyncos.rename(file, destination)
    else:
        await move_existing_file(file, dest, count=count+1)


async def sort(dir: Path):
    files = await all_files(dir)
    docs, pics, progs, archs, vids, auds = await splitup(files)
    if docs:
        docdir = await makedir(dir, "Dokumente")
        for doc in docs:
            await move_file(doc, docdir)
    if pics:
        picdir = await makedir(dir, "Bilder")
        for pic in pics:
            await move_file(pic, picdir)
    if progs:
        progdir = await makedir(dir, "Programme")
        for prog in progs:
            await move_file(prog, progdir)
    if archs:
        archdir = await makedir(dir, "Archive")
        for arch in archs:
            await move_file(arch, archdir)
    if vids:
        viddir = await makedir(dir, "Videos")
        for vid in vids:
            await move_file(vid, viddir)
    if auds:
        auddir = await makedir(dir, "Audios")
        for aud in auds:
            await move_file(aud, auddir)


async def cleanup(directory: Path) -> None:
    for item in directory.iterdir():
        if item.is_dir():
            await cleanup(item)
            try:  # Directory may be empty or we could be blocked from writing.
                item.rmdir()
            except OSError:  # Directory is not empty or blocked, so leave it.
                pass


async def main(directory: Union[Path, str] = downloadDir) -> None:
    if not isinstance(directory, Path):
        directory = Path(directory)
    await sort(directory)
    await cleanup(directory)


def display_results():
    GUI.getPopup("Finished sorting the given Folder.")  # TODO: Rewrite the module to actually display results.


if __name__ == "__main__":
    if len(sys.argv) == 1:
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
