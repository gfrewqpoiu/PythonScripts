import trio
import GUI
import pprint
from trio import Path
from loguru import logger

async def maybe_rename(file: Path, str_to_remove: str):
    if await file.is_file():
        if str_to_remove in file.name:
            fullpath = await file.absolute()
            newname = file.name.replace(str_to_remove, "", 1)
            newpath = fullpath.with_name(newname)
            await fullpath.rename(newpath)

async def main():
    event, values = GUI.getFolderInputWindow(initial_folder=str(await Path.home()))
    if event == "OK":
        folder = values[0]
        try:
            str_to_remove = GUI.getTextInputWindow("mass_rename", "What string do you want to remove from the files?")
        except AttributeError:
            logger.error("Prompt was cancelled by the User.")
            exit(1)
        folder = Path(folder)
        async with trio.open_nursery() as nursery:
            for item in await folder.iterdir():
                nursery.start_soon(maybe_rename, item, str_to_remove)

    else:
        logger.error("Prompt was cancelled by the User.")
        exit(1)


if __name__ == '__main__':
    trio.run(main)
