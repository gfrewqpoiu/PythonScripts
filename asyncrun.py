import asyncio

async def asyncrun(cmd, *args):
    proc = await asyncio.subprocess.create_subprocess_exec(cmd, *args, stdout=asyncio.subprocess.PIPE)
    out = await proc.stdout.read()
    out = out.decode().rstrip()
    await proc.wait()
    return out