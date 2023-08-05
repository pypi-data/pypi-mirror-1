# -*- coding: utf-8 -*-
# Copyright (C)2007 Ingeniweb

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
""" Compute the AST
"""
import md5
import compiler
import os
import logging
import sys
from cPickle import dumps, loads

# XXX cache the codes
registered_code = {}
visited_modules = {}

class CleanNode(object):

    def __init__(self, node, treshold=5):
        code = [str(el) for el in node.getChildren()
                if el is not None and not isinstance(el, basestring)]
        # too small
        self.small = len(code) < treshold
        self.code = ' '.join(code)
        self.name = node.name
        self.filename = node.filename
        self.key = node.key

        if hasattr(node, 'klass'):
            self.klass = node.klass

class CodeSeeker(object):

    def __init__(self, filename, registered_code=None, filtered_functions=None,
                 treshold=1):
        """compiles the AST"""
        self.filename = os.path.realpath(filename)
        self.node = compiler.parseFile(self.filename)
        if registered_code is None:
            self.registered_code = {}
        else:
            self.registered_code = registered_code
        self.treshold = treshold
        if filtered_functions is None:
            self.filtered_functions = tuple()
        else:
            self.filtered_functions = filtered_functions
        compiler.walk(self.node, self)

    def _key(self, node):
        """calculates an unique key for a node"""
        if hasattr(node, 'klass'):
            return '%s %s.%s:%s' % (node.filename, node.klass,
                                    node.name, node.lineno)
        else:
            return '%s %s:%s' % (node.filename, node.name, node.lineno)

    def _clean(self, node):
        """returns a clean node"""
        return CleanNode(node, self.treshold)

    def register(self, node):
        """register the node"""
        node.filename = self.filename
        node.key = self._key(node)
        node = self._clean(node)
        if not node.small:
            self.registered_code[node.key] = node

    #
    # compiler walker APIs
    #
    def visitFunction(self, t):
        if t.name in self.filtered_functions:
            return
        self.register(t)

    def visitClass(self, t):
        for subnode in t.getChildren():
            if not subnode.__class__ in  (compiler.ast.Stmt,
                                          compiler.ast.Function):
                continue
            for f in subnode.getChildren():
                if f is None or isinstance(f, str):
                    continue
                f.klass = t.name
                self.visit(f)

def register_module(filename, filtered_functions=None, treshold=1):
    """registers a module"""
    if already_visited(filename):
        return
    CodeSeeker(filename, registered_code, filtered_functions, treshold)
    visited(filename)

def already_visited(filename):
    if filename not in visited_modules:
        return False
    key = md5.md5(open(filename).read()).hexdigest()
    return visited_modules[filename] == key

def visited(filename):
    visited_modules[filename] = md5.md5(open(filename).read()).hexdigest()


def register_folder(folder, extensions=('py',), filtered_files=None,
                    filtered_folders=None, filtered_functions=('__init__',),
                    treshold=5):
    """walk a folder and register python modules"""
    if filtered_files is None:
        filtered_files = tuple()
    if filtered_folders is None:
        filtered_folders = tuple()
    if filtered_functions is None:
        filtered_functions = tuple()

    for root, dirs, files in os.walk(folder):
        if os.path.split(root)[-1] in filtered_folders:
            continue
        for file in files:
            extension = file.split('.')[-1]
            if extension in  extensions and file not in filtered_files:
                register_module(os.path.join(root, file),
                                filtered_functions, treshold)

def enable_log():
    """enable logging"""
    console = logging.StreamHandler(sys.stdout)
    console.setLevel(logging.INFO)
    formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
    console.setFormatter(formatter)
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    root.addHandler(console)

def save_register(filename):
    dump = dumps((registered_code, visited_modules))
    f = open(filename, 'w')
    try:
        f.write(dump)
    finally:
        f.close()

def load_register(filename):
    dump = open(filename).read()
    global registered_code
    global visited_modules
    registered_code, visited_modules = loads(dump)

