import sys

if __name__ == '__main__':
    link = sys.argv[1]
    link = link.split("/")
    import pprint

    link.remove('')
    if 'folder' in link:
        raise AttributeError("Folder links are not supported.")
    if 'file' in link:
        link.remove('file')
    if 'd' in link:
        link.remove('d')

    pprint.pprint(link)

    if "?id=" not in link[2]:
        id = link[2]
    else:
        id = link[2].split("=")[1]

    targetlink = f"https://drive.google.com/uc?export=download&id={id}"
    print(targetlink)
