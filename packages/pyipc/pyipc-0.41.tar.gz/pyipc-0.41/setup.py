#!/usr/bin/env python
from distutils.core import Extension, setup

__revision__ = "$Id: setup.py 151 2006-07-19 21:24:45Z const $"

ipc = Extension(
    name = "ipc",
    sources = ["ipc.c"],
    )

classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: Python Software Foundation License",
    "Natural Language :: English",
    "Operating System :: POSIX",
    "Programming Language :: C",
    "Topic :: Software Development :: Libraries :: Python Modules",
    ]

setup(
    name = "pyipc",
    version = "0.41",
    license = "PSF",
    description = "Python bindings to System V IPC",
    long_description = """\
Python bindings to System V interprocess communication mechanisms:
- Message Queues
- Semaphores
- Shared Buffers""",
    author = "Constantin Baranov",
    author_email = "baranov86@mail.ru",
    url = "http://const.tltsu.ru/",
    download_url = "http://const.tltsu.ru/svn/const/pub/pyipc/",
    platforms = ["posix"],
    ext_modules = [ipc],
    classifiers = classifiers,
    )
