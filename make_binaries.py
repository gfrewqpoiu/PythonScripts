import PyInstaller.__main__
import os

import distutils
if distutils.distutils_path.endswith('__init__.py'):
    distutils.distutils_path = os.path.dirname(distutils.distutils_path)


def make_bin_windowed(binaryname: str):
    PyInstaller.__main__.run([
        '--onefile',
        '--windowed',
        '--hidden-import=distutils',
        '--clean',
        '-y',
        f'{binaryname}.py'
    ])


def make_bin(binaryname: str):
    PyInstaller.__main__.run([
        '--onefile',
        '--console',
        '--hidden-import=distutils',
        '--clean',
        '-y',
        f'{binaryname}.py'
    ])


if __name__ == '__main__':
    make_bin_windowed('mass_rename')
    make_bin('drive_direct_download')