import sys

import GUI
import asyncrun


async def check_for_command(cmd: str):
    """Checks if the given command is installed."""
    try:
        await asyncrun.asyncrun(cmd)
        return True
    except FileNotFoundError:
        return False


async def main():
    GUI.getPopup('This program will install some helpful tools for Python development in Windows')
    if not check_for_command("python3"):
        if not check_for_command("choco"):
            GUI.getErrorWindow("You don't have Python 3 or chocolatey installed. Install either to continue.")
            sys.exit(1)
        else:
            await asyncrun.asyncrun('choco', 'install', 'python', '-y')
    await asyncrun.asyncrun('python3', '-m', 'pip', 'install', '--upgrade', 'prompt-toolkit', 'pipenv', 'xonsh')
