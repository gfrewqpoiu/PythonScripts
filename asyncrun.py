import asyncio
import logging
from typing import List

log = logging.getLogger()


async def convert_args_to_str(*args) -> List[str]:
    newargs: List[str] = []
    for arg in args:
        if not isinstance(arg, str):
            newargs.append(str(arg))
        else:
            newargs.append(arg)
    return newargs


async def asyncrun(cmd: str, *args) -> str:
    """Runs the given command, connects stdout to the current shell and waits until it is completed"""
    log.info(f"Running cmd {cmd} with {list(args)}")
    newargs: List[str] = await convert_args_to_str(*args)
    proc = await asyncio.subprocess.create_subprocess_exec(cmd, *newargs, stdout=asyncio.subprocess.PIPE)
    out = await proc.stdout.read()
    out = out.decode().rstrip()
    await proc.wait()
    return out


async def asyncrun_quiet(cmd: str, *args) -> str:
    """Runs the given command quietly and waits until it is completed."""
    log.debug(f"Quietly Running cmd {cmd} with {list(args)}")
    newargs: List[str] = await convert_args_to_str(*args)
    proc = await asyncio.subprocess.create_subprocess_exec(cmd, *newargs, stdout=asyncio.subprocess.PIPE,
                                                           stderr=asyncio.subprocess.DEVNULL)
    out = await proc.stdout.read()
    out = out.decode().rstrip()
    await proc.wait()
    return out
