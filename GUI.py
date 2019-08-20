import os
import pprint
from pathlib import Path

import PySimpleGUIQt as sg

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


def getInputWindow(titletext="Inputfile"):
    layout = [[sg.Text("Select a file to convert:")],
              [sg.Input(), sg.FileBrowse("Select File", initial_folder=home)],
              [sg.OK(), sg.Cancel()]]
    window = sg.Window(titletext, layout)
    event, values = window.Read()
    window.Close()
    return event, values


def getFolderInputWindow(titletext="Inputfolder", initial_folder=home):
    layout = [[sg.Text("Select a folder:")],
              [sg.Input(), sg.FolderBrowse("Select Folder", initial_folder=initial_folder)],
              [sg.OK(), sg.Cancel()]]
    window = sg.Window(titletext, layout)
    event, values = window.Read()
    window.Close()
    return event, values


def getOutputWindow(titletext="Outputfile", prefill=""):
    layout = [[sg.Text("Where should it be saved?")],
              [sg.Text("Save under:"), sg.Input(), sg.FileSaveAs(initial_folder=prefill)],
              [sg.OK(), sg.Cancel()]]
    window = sg.Window(titletext, layout)
    event, values = window.Read()
    window.Close()
    return event, values


def getErrorWindow(text="Error"):
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


def rcloneoutputwindow(contents: []):
    output = ""
    for item in contents:
        output += item.name + "\n"
    layout = [[sg.Text("Here are the contents:")],
              [sg.MultilineOutput(output)],
              [sg.OK()]]
    window = sg.Window("Results", layout)
    window.Read()
    window.Close()


def sortoutputwindow(contents: [str]):
    output = ""
    for item in contents:
        output += item + "\n"
    layout = [[sg.Text("I have sorted these files:")],
              [sg.MultilineOutput(output)],
              [sg.OK()]]
    window = sg.Window("Results", layout)
    window.Read()
    window.Close()


if __name__ == '__main__':
    pprint.pprint(home)
    pprint.pprint(getInputWindow())
    pprint.pprint(getOutputWindow(prefill=""))
