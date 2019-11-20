import sys

if __name__ == '__main__':
    link = sys.argv[1]
    link = link.split("/")
    import pprint
    pprint.pprint(link)
    targetlink = f"https://drive.google.com/uc?export=download&id={link[5]}"
    print(targetlink)