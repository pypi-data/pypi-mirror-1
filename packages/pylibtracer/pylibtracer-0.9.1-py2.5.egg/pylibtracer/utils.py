#!/usr/bin/env python
# encoding: utf-8
"""
utils.py

Created by Olli Wang (olliwang@ollix.com) on 2009-11-26.
Copyright (c) 2009 Ollix. All rights reserved.
"""

import os
import sys
import py_compile

__all__ = ['import_module', 'iter_dir_filenames', 'splitext', 'compile_py']

class UselessStd:
    def write(self, message): pass

def import_module(module_path):
    """Import a module by specified module path"""
    savestdout, savestderr = sys.stdout, sys.stderr
    sys.stdout, sys.stderr = [UselessStd()] * 2
    try:
        if sys.platform.startswith('java'):
            import java
            while True:
                try:
                    module = __import__(module_path)
                except java.lang.ExceptionInInitializerError:
                    continue
                else:
                    break
        else:
            module = __import__(module_path)
    finally:
        sys.stdout, sys.stderr = savestdout, savestderr
    # For Jython: Raise error if imported module is a Java class
    if repr(module).startswith("<java package "):
        raise ImportError
    # Get the real module object
    try:
        for submodule_name in module_path.split('.')[1:]:
            module = getattr(module, submodule_name)
    except AttributeError:
        raise ImportError
    return module

def iter_dir_filenames(dirname, ignore_hidden_file=True):
    """Iterate filenames under a certain directoy."""
    for root, dirnames, basenames in os.walk(dirname):
        for basename in basenames:
            if ignore_hidden_file and basename.startswith('.'):
                continue
            yield os.path.join(root, basename)

def splitext(filename):
    """Split the extension from a filename.

    Behavior like os.path.splitext unless it treats $py.class as a extension.

    Returns:
        "(root, ext)", either part may be empty
    """
    if filename.endswith('$py.class'):
        root = filename.rsplit('$py.class')[0]
        ext = '$py.class'
    else:
        root, ext = os.path.splitext(filename)
    return (root, ext)

def compile_py(filename, compiled_ext='.pyc'):
    """Compile Python module from a filename.

    Args:
        filename: The Python module to be compiled.
        compiled_ext: The filename extension for compiled modules.

    Returns:
        Compiled module filename or original filename if failed to compile.
    """
    root, ext = splitext(filename)
    compiled_filename = root + compiled_ext
    if ext == '.py' and os.path.isfile(filename):
        try:
            py_compile.compile(filename)
        except IOError:
            if os.path.isfile(compiled_filename):
                filename = compiled_filename
        else:
            filename = compiled_filename
    return filename

