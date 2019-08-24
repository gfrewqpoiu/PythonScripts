import asyncio
import pickle
from collections import deque
import PySimpleGUIQt
from cloudconvert import Job as Job

host = "127.0.0.1"
Print = PySimpleGUIQt.EasyPrint

async def get_queue(host: str) -> deque:
    reader, writer = await asyncio.open_connection(host, 8890)
    data = await reader.read()
    queue = pickle.loads(data)
    return queue


async def main():
    queue = await get_queue(host)
    Print("Currently running Job:")
    Print(str(queue.popleft()))
    Print("Other Jobs:")
    for item in queue:
        Print(str(item))
    if PySimpleGUIQt.DebugWin.debug_window is not None:
        event, values = PySimpleGUIQt.DebugWin.debug_window.window.Read()
        if event == 'Quit':
            PySimpleGUIQt.DebugWin.Close()


if __name__ == '__main__':
    asyncio.run(main())
