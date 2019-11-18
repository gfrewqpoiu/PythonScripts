import asyncio
import subprocess
import trio
from loguru import logger
from typing import List
log = logger


async def convert_args_to_str(*args) -> List[str]:
    newargs: List[str] = []
    for arg in args:
        if not isinstance(arg, str):
            newargs.append(str(arg))
        else:
            newargs.append(arg)
    return newargs

async def _asyncrun_trio(cmd: str, args: List[str]) -> str:
    command: List[str] = [cmd]
    command.extend(args)
    out = await trio.run_process(command=command, capture_stdout=True)
    return out.stdout


async def asyncrun_trio(cmd: str, *args) -> str:
    log.debug(f"Using trio to run cmd {cmd} with {list(args)}")
    newargs = await convert_args_to_str(*args)
    out = trio.run(_asyncrun_trio, cmd, newargs)
    return out

async def asyncrun(cmd: str, *args) -> str:
    """Runs the given command, connects stdout to the current shell and waits until it is completed"""
    log.info(f"Running cmd {cmd} with {list(args)}")
    return await asyncrun_trio(cmd, *args)


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
