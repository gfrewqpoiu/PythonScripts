import trio
import GUI
import pprint
from trio import Path
from loguru import logger


async def replace_substr(file: Path, str_to_search_for: str, replace_with: str):
    if await file.is_file():
        if str_to_search_for in file.name:
            fullpath = await file.absolute()
            newname = file.name.replace(str_to_search_for, replace_with, 1)
            newpath = fullpath.with_name(newname)
            await fullpath.rename(newpath)


async def maybe_rename(file: Path, str_to_remove: str):
    await replace_substr(file, str_to_remove, "")


async def remove_first_str():
    folder, recursive = GUI.getFolderRecursiveWindow(title_text="Remove first occurrence",
                                                 initial_folder=str(await Path.home()))
    folder = Path(folder)
    str_to_remove = GUI.getTextInputWindow("Remove first occurrence" , "What do you want to remove from the filenames?")
    async with trio.open_nursery() as nursery:
        for item in await folder.iterdir():
            nursery.start_soon(maybe_rename, item, str_to_remove)


async def replace_str():
    event, values = GUI.getFolderInputWindow(initial_folder=str(await Path.home()))
    if event == "OK":
        folder = values[0]
        try:
            fromstr, tostr = GUI.getDualTextInputWindow("Replace String",
                                                        "What do you want to replace?",
                                                        "With what do you want to replace that?")
        except AttributeError:
            logger.error("Prompt was cancelled by the User.")
            exit(1)

        folder = Path(folder)
        async with trio.open_nursery() as nursery:
            for item in await folder.iterdir():
                nursery.start_soon(replace_substr, item, fromstr, tostr)


async def main():
    functions = ["Remove first occurrence", "Replace substring"]
    func = GUI.getButtonWindow("Mass Renamer", functions)
    if func == "Remove first occurrence":
        await remove_first_str()
    if func == "Replace substring":
        await replace_str()


if __name__ == '__main__':
    trio.run(main)
