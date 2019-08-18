import asyncio
import logging

log = logging.getLogger()

async def asyncrun(cmd, *args):
    """Runs the given command, connects stdout to the current shell and waits until it is completed"""
    log.info(f"Running cmd {cmd} with {list(args)}")
    proc = await asyncio.subprocess.create_subprocess_exec(cmd, *args, stdout=asyncio.subprocess.PIPE)
    out = await proc.stdout.read()
    out = out.decode().rstrip()
    await proc.wait()
    return out


async def asyncrun_quiet(cmd, *args):
    """Runs the given command quietly and waits until it is completed."""
    log.debug(f"Quietly Running cmd {cmd} with {list(args)}")
    proc = await asyncio.subprocess.create_subprocess_exec(cmd, *args, stdout=asyncio.subprocess.DEVNULL,
                                                           stderr=asyncio.subprocess.DEVNULL)
    await proc.wait()
