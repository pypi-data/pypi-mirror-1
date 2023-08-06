import os
import sys

def whereampy(path):
    '''Given a path, returns a list of strings describing it.'''
    if os.path.exists(path):
        yield 'exists'
    else:
        yield 'does not exist'
        return # die now

    real = os.path.realpath(path)
    if real != path:
        yield 'has the real path: %s' % real

    if os.path.isfile(real):
        yield 'is a file (checking directory now)'
        real = os.path.split(real)[0]

    abs = os.path.abspath(real)
    yield 'has absolute path: %s' % abs

    if any((abs == os.path.abspath(os.path.realpath(p)) for p in sys.path)):
        yield 'is in sys.path'

    files = os.listdir(abs)
    if 'setup.py' in files:
        yield 'is a distribution root (has a setup.py file)'
    if '__init__.py' in files:
        yield 'is a package (has an __init__.py file)'
