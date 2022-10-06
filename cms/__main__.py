from sys import path, version_info, exit, argv
import os

if __package__ == '':
    # load local package
    path.insert(0, './')

from cms.engine import Engine

e = Engine(argv[1],  argv[2])
