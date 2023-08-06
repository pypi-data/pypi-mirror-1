#!/usr/bin/env python

from distutils.core import setup
import py2exe
import sys

from getmps import VERSION

NAME = 'getmps'
WIN_BINARY = '%s-%s-bin-mswin' % (NAME, VERSION,)
DIST_DIR = 'dist\\%s' % (WIN_BINARY)
DESCRIPTION = '''\
A Windows command-line tool to look up UK Members of Parliament by postcode
'''

py2exe_options = dict(
    dist_dir=DIST_DIR,
    optimize=2,
    excludes=[
        # silence some warnings of missing modules
        '_imaging_gif',
        'dummy.Process',
        'email',
        'email.utils',
        'email.Utils',
        'ICCProfile',
        'Image',
        '_scproxy',

        # filter out unused .pyd files
        '_ssl',
        '_imaging',
        '_hashlib',
        'pyexpat',
        'win32api',
        'bz2',
        '_multiprocessing',
        'win32pipe',
        'select',

        # filter out unused .pyo files in library.zip
        'doctest',
        'pyglet.window.xlib',
        'pyglet.window.carbon',
        'pyglet.window.carbon.constants',
        'pyglet.window.carbon.types',
        'win32con',
    ],
    dll_excludes=["pywintypes26.dll"],
)

config = dict(
    # pypi
    author='Jonathan Hartley',
    author_email='tartley@tartley.com',
    classifiers = [
        "Development Status :: 2 - Pre-Alpha",
        "Environment :: Console",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: BSD License",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.6",
        "Topic :: Other/Nonlisted Topic",
    ],
    description=DESCRIPTION,
    license='New BSD License',
    long_description='', #get_long_description(),
    name=NAME,
    packages=['twfy'],
    provides=[NAME],
    py_modules=[],
    scripts=['getmps.py'],
    # install_requires=['mock'], # setuptools only
    url='http://code.google.com/p/%s' % (NAME,),
    version=VERSION,

    # py2exe
    console=['getmps.py'],
    options=dict(
        py2exe=py2exe_options
    ),
)


def main():
    if not ('--verbose' in sys.argv or '-v' in sys.argv):
        sys.argv.append('--quiet')
    setup(**config)


if __name__ == '__main__':
    main()

