import aiohttp
from bs4 import BeautifulSoup
import asyncio
import webbrowser
import aiofiles as files
import pprint
import requests


def fetch(session: requests.Session, url: str) -> str:
    with session.get(url) as response:
        return response.text


def save(session: requests.Session, url: str, filename: str = "Test.mp4"):
    with open(filename, "wb") as file:
        with session.get(url, stream=True) as response:
            for chunk in response.iter_content(chunk_size=4096):
                file.write(chunk)


def main(link: str):
    with requests.Session() as session:
        html = fetch(session, link)
        soup = BeautifulSoup(html, 'lxml')
        source = soup.find('source')
        targetlink = source.get('src')
        print("Got link: " + targetlink)
        save(session, targetlink)


if __name__ == '__main__':
    main(link="")
