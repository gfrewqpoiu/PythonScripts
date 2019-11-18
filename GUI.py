import os
import pprint
from rclone import RcloneItem
from pathlib import Path
from typing import List, Tuple, Dict
import sys
if sys.platform == "darwin":
    import PySimpleGUIQt as sg  # type: ignore
else:
    import PySimpleGUI as sg  # type: ignore

home = os.fsdecode(Path.home())


def getInputOutputWindow(titletext="Select File"):
    layout = [[sg.Text('Input File')],
              [sg.Input(), sg.FileBrowse(initial_folder=home)],
              [sg.Text('Output File')],
              [sg.Input(), sg.FileSaveAs(initial_folder=home)],
              [sg.OK(), sg.Cancel()]]
    window = sg.Window(titletext, layout)
    event, values = window.Read()
    return event, values


def getInputWindow(titletext: str = "Input File"):
    layout = [[sg.Text("Select a file to convert:")],
              [sg.Input(), sg.FileBrowse("Select File", initial_folder=home)],
              [sg.OK(), sg.Cancel()]]
    window = sg.Window(titletext, layout)
    event, values = window.Read()
    window.Close()
    return event, values


def getFolderInputWindow(titletext: str = "Input Folder", initial_folder: str = home) -> Tuple[str, Dict[str, str]]:
    layout = [[sg.Text("Select a folder:")],
              [sg.Input(), sg.FolderBrowse("Select Folder", initial_folder=initial_folder)],
              [sg.OK(), sg.Cancel()]]
    window = sg.Window(titletext, layout)
    event, values = window.Read()
    window.Close()
    return event, values


def getFolderRecursiveWindow(title_text: str = "Input Folder", initial_folder: str = home, recuse_text: str = "Include subdirectories?") -> Tuple[str, bool]:
    layout = [[sg.Text("Select a folder:")],
              [sg.Input(key="_FOLDER_"), sg.FolderBrowse("Select Folder", initial_folder=initial_folder)],
              [sg.Checkbox(recuse_text, key="_RECURSIVE_")],
              [sg.OK(), sg.Cancel()]]
    window = sg.Window(title_text, layout)
    event, values = window.Read()
    window.Close()
    if event == "OK":
        return values["_FOLDER_"], bool(values["_RECURSIVE_"])
    else:
        raise AttributeError("The user cancelled the Input Prompt.")


def getOutputWindow(titletext: str = "Output File", prefill: str = ""):
    layout = [[sg.Text("Where should it be saved?")],
              [sg.Text("Save under:"), sg.Input(), sg.FileSaveAs(initial_folder=prefill)],
              [sg.OK(), sg.Cancel()]]
    window = sg.Window(titletext, layout)
    event, values = window.Read()
    window.Close()
    return event, values


def getErrorWindow(text: str = "Error"):
    sg.PopupError(text)


def getPopup(text: str):
    sg.Popup(text)


def rclonewindow():
    layout = [[sg.Text("What is the Drive you want to access?")],
              [sg.Input("Drive")],
              [sg.Text("What is the folder you want to see?")],
              [sg.Input()],
              [sg.Cancel(), sg.OK()]]
    window = sg.Window("rclone", layout=layout)
    event, values = window.Read()
    window.Close()
    return event, values


def rcloneoutputwindow(contents: List[RcloneItem]):
    layout = [[sg.Text("Here are the contents:")],
              [sg.Listbox(contents)],
              [sg.OK()]]
    window = sg.Window("Results", layout)
    window.Read()
    window.Close()


def sortoutputwindow(contents: List[str]):
    output = "\n".join(contents)
    layout = [[sg.Text("I have sorted these files:")],
              [sg.MultilineOutput(output)],
              [sg.OK()]]
    window = sg.Window("Results", layout)
    window.Read()
    window.Close()


def getTextInputWindow(title: str = "Title", text: str = "Text") -> str:
    layout = [[sg.Text(text)],
              [sg.InputText(key="_INPUT_")],
              [sg.Cancel(), sg.OK()]]
    window = sg.Window(title, layout)
    event, values = window.Read()
    window.Close()
    if event == "OK":
        return values["_INPUT_"]
    else:
        raise AttributeError("The user cancelled the Input Prompt.")


def getDualTextInputWindow(title: str, field_1: str, field_2: str) -> Tuple[str, str]:
    layout = [[sg.Text(field_1)],
              [sg.InputText(key="_INPUT1_")],
              [sg.Text(field_2)],
              [sg.InputText(key="_INPUT2_")],
              [sg.Cancel(), sg.OK()]]
    window = sg.Window(title, layout)
    event, values = window.Read()
    window.Close()
    if event == "OK":
        return values["_INPUT1_"], values["_INPUT2_"]
    else:
        raise AttributeError("The user cancelled the Input Prompt.")


def getButtonWindow(title: str, buttons: List[str]) -> str:
    layout = []
    for elem in buttons:
        layout.append([sg.Button(elem)])
    layout.append([sg.Cancel()])
    window = sg.Window(title, layout=layout)
    event, values = window.Read()
    window.Close()
    if not event == "Cancel":
        return event
    else:
        raise AttributeError("The user cancelled the Prompt.")


if __name__ == '__main__':
    pass
