import trio
import GUI
import pprint
from pathlib import Path


async def main():
    event, values = GUI.getFolderInputWindow(initial_folder=str(Path.home()))
    if event == "OK":
        folder = values[0]

if __name__ == '__main__':
    trio.run(main)
