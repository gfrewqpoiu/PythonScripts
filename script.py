import sys

if sys.platform != 'darwin':
    raise EnvironmentError("This script only works in macOS!")
import appscript
import pprint

if __name__ == "__main__":
    brave = appscript.app('Brave Browser')
    window = brave.windows[1]
    for tab in window.tabs.get():
        pprint.pprint(tab.URL.get())
    url = window.active_tab.URL.get()
    pprint.pprint(url)
