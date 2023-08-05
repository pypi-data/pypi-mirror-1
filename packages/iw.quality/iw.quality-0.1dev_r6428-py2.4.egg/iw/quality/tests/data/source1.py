import compiler
import os
import logging

def register_module(filename):
    """registers a module"""
    logging.info('Registering %s' % filename)
    CodeSeeker(filename)

def register_folder(folder):
    """walk a folder and register python modules"""
    for root, dirs, files in walk(folder):
        for file in files:
            if file.endswith('.py'):
                register_module(os.path.join(root, file))

def enable_log():
    import sys
    console = logging.StreamHandler(sys.stdout)
    console.setLevel(logging.DEBUG)
    console.setFormatter(formatter)
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    root.addHandler(console)

