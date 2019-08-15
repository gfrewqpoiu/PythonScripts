import asyncio
import sys
from asyncrun import asyncrun_quiet


async def convert(input, output, preset='Fast 1080p30', quality="22.0", speed="medium"):
    await asyncrun_quiet('HandBrakeCLI', '-i', input, '-o', output, '-O',
                   '-Z', preset, '--quality', quality, '--encoder-preset', speed)


async def main(input, output):
    await convert(input, output)


if __name__ == '__main__':
    asyncio.run(main(sys.argv[1], sys.argv[2]))
