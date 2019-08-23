import asyncio
import pathlib
import sys

from asyncrun import asyncrun_quiet


async def convert(input, output, preset='Fast 1080p30', quality="22.0", speed="slow"):
    if isinstance(input, pathlib.Path):
        input = str(input)
    if isinstance(output, pathlib.Path):
        output = str(output)
    await asyncrun_quiet('HandBrakeCLI', '-i', input, '-o', output, '-O',
                   '-Z', preset, '--quality', quality, '--encoder-preset', speed)


async def main(input, output):
    await convert(input, output)


def getfiles():
    import GUI
    import os.path
    event, input = GUI.getInputWindow()
    if event == 'OK':
        inputfile, ext = os.path.splitext(input[0])
        inputfile += ".mp4"
        event, output = GUI.getOutputWindow(prefill=inputfile)
        if event == 'OK':
            asyncio.run(main(input[0], output[0]))

if __name__ == '__main__':
    if len(sys.argv) == 3:
        asyncio.run(main(sys.argv[1], sys.argv[2]))
    else:
        getfiles()
