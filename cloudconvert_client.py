import asyncio
import pickle
import PySimpleGUI as sg  # type: ignore
from cloudconvert import Job as Job
from typing import Deque, Union, List
import pprint

host = "185.223.29.82"


async def get_queue(ip: str = host, port: Union[int, str] = 8890) -> Deque[Job]:
    reader, writer = await asyncio.open_connection(ip, port)
    data = await reader.read()
    queue = pickle.loads(data)
    return queue


async def main() -> None:
    queue = await get_queue(host)  # type: Deque[Job]
    output = ["Currently Running Job:", str(queue.popleft()), "Other Jobs:"]  # type: List[Union[str, Job]]
    output.extend(queue)
    layout = [[sg.Text("Here are the jobs:")],
              [sg.Listbox(output)],
              [sg.CloseButton("Close")]]

    window = sg.Window(title="Cloud Convert Client", layout=layout)
    event, values = window.Read()
    pprint.pprint(event)
    pprint.pprint(values)


if __name__ == '__main__':
    asyncio.run(main())
