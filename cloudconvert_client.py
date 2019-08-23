import asyncio
import pickle
from collections import deque

host = "127.0.0.1"


async def get_queue(host: str) -> deque:
    reader, writer = await asyncio.open_connection(host, 8890)
    data = await reader.read()
    queue = pickle.loads(data)
    return queue


async def main():
    queue = await get_queue(host)
    print("Currently running Job:")
    print(str(queue.popleft()))
    print("Other Jobs:")
    for item in queue:
        print(str(item))


if __name__ == '__main__':
    asyncio.run(main())
