from bs4 import BeautifulSoup
import requests
from pathlib import Path
from typing import Optional
import sys


def fetch(session: requests.Session, url: str) -> str:
    with session.get(url) as response:
        return response.text


def save(session: requests.Session, url: str, filename: str = "Test.mp4") -> None:
    with open(filename, "wb") as file:
        with session.get(url, stream=True) as response:
            for chunk in response.iter_content(chunk_size=4096):
                file.write(chunk)


def cleanup_title(title: str) -> str:
    new_title = title.replace("<title>", "")
    new_title = new_title.replace("</title>", "")
    new_title += ".mp4"
    return new_title


def main(link: Optional[str] = None) -> None:
    if link is None:
        print("Please provide the link")
        link = input().strip()
    with requests.Session() as session:
        html = fetch(session, link)
        soup = BeautifulSoup(html, 'lxml')
        title = str(soup.find('title'))
        newtitle = cleanup_title(str(title))
        source = soup.find('source')
        targetlink = source.get('src')
        print("Got link: " + targetlink)
        filename = Path(Path.home().absolute(), "Downloads/", newtitle)
        save(session, targetlink, filename=str(filename))
        if sys.platform == "darwin":
            import rumps
            rumps.notification("Parse_Website.py", "Done", "Downloaded the video")


if __name__ == '__main__':
    main()
