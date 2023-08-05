#!/usr/bin/env python
from distutils.core import Extension, setup

__revision__ = "$Id: setup.py 2 2005-07-31 20:41:23Z root $"

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
    version = "0.2",
    license = "PSF",
    description = "IPC bindings for Python",
    long_description = """\
System V IPC bindings for Python:
  - message queues
  - semaphores
""",
    author = "Constantin Baranov",
    author_email = "baranov86@mail.ru",
    url = "http://tltsu.ru/~const/",
    platforms = ["posix"],
    ext_modules = [ipc],
    classifiers = classifiers,
    )
