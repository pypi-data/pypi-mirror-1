#!/usr/bin/env python
# encoding: utf-8
"""
libtracer.py

Created by Olli Wang (olliwang@ollix.com) on 2009-11-21.
Copyright (c) 2009 Ollix. All rights reserved.
"""

import os
import sys
import types
import shutil
import zipfile

from pylibtracer import utils


class LibTracer(object):
    """Traces all required Python modules from a certain directory."""

    python_compiled_exts = ['.pyc', '.so']
    jython_compiled_exts = ['$py.class']

    ignored_module_paths = ['ez_setup', 'setup']
    ignored_module_attribute_names = ['__builtins__', '__doc__', '__name__']

    def __init__(self, basedir='.', full_packages=None, ignore_packages=None,
                 ignore_test=True, ignore_standard_library=True, quiet=False):
        """Initialize a LibTracer instance.

        Args:
            basedir: The directory for searching.
            full_packages: A list of packages should be included explicitly.
            quiet: If True, be quiet during collecting.

        Raises:
            OSError: Raised if the specified `basedir` is not a directory.
        """
        # Raise error if specified `basedir` is not a directory
        if not os.path.isdir(basedir):
            raise OSError("No such directory: %r" % basedir)

        # Convert `basedir` to absolute path
        if os.path.isabs(basedir):
            self.basedir = basedir
        else:
            self.basedir = os.path.abspath(basedir)

        # Create a list of system paths appending specified directory
        sys.path.insert(0, self.basedir)
        self.sys_path = sys.path[:]
        # Remove standard library's syspath
        if ignore_standard_library:
            standard_library_syspath = os.path.dirname(os.__file__)
            if standard_library_syspath == '__pyclasspath__':
                standard_library_syspath += '/'
            self.sys_path.remove(standard_library_syspath)

            # Remove further directories in standard library
            if os.path.isdir(standard_library_syspath):
                for name in os.listdir(standard_library_syspath):
                    if name == 'site-packages':
                        continue
                    dirname = os.path.join(standard_library_syspath, name)
                    if os.path.isdir(dirname) and dirname in self.sys_path:
                        self.sys_path.remove(dirname)

        # Valid filename extension
        if sys.platform.startswith('java'):
            self.valid_exts = self.jython_compiled_exts
            self.invalid_exts = self.python_compiled_exts
        else:
            self.valid_exts = self.python_compiled_exts
            self.invalid_exts = self.jython_compiled_exts
        self.compiled_ext = self.valid_exts[0]

        if ignore_packages is None:
            ignore_packages = []

        self.ignore_packages = ignore_packages
        self.ignore_test = ignore_test
        self.quiet = quiet
        self.__full_packages = full_packages if full_packages else []
        self.__found_paths = []
        self.__found_module_paths = []
        self.__module_paths = self.__find_module_paths(self.basedir)

    def __convert_filename_to_module_path(self, filename):
        """Convert specified filename to module path.

        The specified filename should be an absolute path and end with
        accepted extensions.

        Args:
            filename: The filename to be converted to module path.

        Returns:
            A string of the converted module path such as `some.module`.

        Raises:
            OSError: Raised if specified filename is invalid.
        """
        # Remove extension name
        valid_exts = self.valid_exts[:]
        valid_exts.insert(0, '.py')
        for extension in valid_exts:
            if filename.endswith(extension):
                filename = filename.rsplit(extension, 1)[0]
                break
        else:
            raise OSError("The filename extension must be one of %r" % \
                          valid_exts)

        try:
            for sys_path in self.sys_path:
                # Convert to module path
                if filename.startswith(sys_path):
                    # Remove system path directory
                    filename = filename.split(sys_path, 1)[1]
                    # Remove leading seprator
                    filename = filename.split(os.path.sep, 1)[1]
                    # Replace all seprators with a dot (.)
                    filename = filename.replace(os.path.sep, '.')
                    return filename
            else:
                return None
        except IndexError:
            raise OSError("Could not find the module path for %r" % filename)

    def __module_in_full_packages(self, module_path):
        """Determine if a module and its ancestors included in full packages

        Args:
            module_path: The module path to evaluate.

        Returns:
            True or False
        """
        while True:
            if module_path in self.__full_packages:
                return True
            if '.' not in module_path:
                break
            module_path = module_path.rsplit('.', 1)[0]
        return False

    def __find_module_paths(self, path):
        """Find module paths recursively.

        Args:
            path: Could be directory path, file path or module path.

        Returns:
            A list of found module paths.
        """
        if not path or path in self.__found_paths:
            return

        # Find all modules if path is a directory
        if os.path.isdir(path):
            self.__found_paths.append(path)
            for filename in utils.iter_dir_filenames(path):
                # FIXME (olliwang): should support all accepted extensions
                if not filename.endswith('.py'):
                    continue
                if not os.path.isabs(filename):
                    filename = os.path.abspath(filename)
                self.__find_module_paths(filename)
            return
        # Convert to module path if path is a file
        elif os.path.isfile(path):
            self.__found_paths.append(path)
            module_path = self.__convert_filename_to_module_path(path)
            if not module_path:
                return
        else:
            try:
                # Try to get module path from an egg file
                module_path = self.__convert_filename_to_module_path(path)
            except OSError:
                # Specified path is module path
                module_path = path
            else:
                if not module_path:
                    return

        # Return if ignoring test package
        if self.ignore_test and 'test' in module_path.split('.'):
            return

        # Rename module path if ends with `.__init__`
        if module_path.endswith('.__init__'):
            module_path = module_path.rsplit('.__init__', 1)[0]

        # Ignore found and ignored modules
        if module_path in self.__found_module_paths \
           or module_path in self.ignored_module_paths:
            return

        # Import module by `module_path`
        try:
            module = utils.import_module(module_path)
        except:
            return
        self.__found_module_paths.append(module_path)

        package_name = module_path.split('.', 1)[0]
        # Return if module's package in ignored packages.
        if package_name in self.ignore_packages:
            return

        # Include full package
        if package_name not in self.__full_packages:
            package = utils.import_module(package_name)
            try:
                root, ext = utils.splitext(package.__file__)
            except AttributeError:
                # Ignore built-in modules
                pass
            else:
                if package_name != '__init__' and root.endswith('__init__') \
                   and package_name not in self.__full_packages:
                    self.__full_packages.append(package_name)
                    self.__find_module_paths(os.path.dirname(root))

        # Find modules recursively
        for attribute_name in dir(module):
            if attribute_name in self.ignored_module_attribute_names:
                continue
            try:
                attribute = getattr(module, attribute_name)
            except AttributeError:
                continue

            # Find module path for each attribute
            if isinstance(attribute, types.ModuleType) and \
               hasattr(attribute, '__file__'):
                path = attribute.__file__
            elif hasattr(attribute, '__module__'):
                path = attribute.__module__
            else:
                continue

            # Find modules recursively
            self.__find_module_paths(path)

    def get_file_locations(self, compile_all=False):
        """Get file locations with system path and its relative path.

        Returns:
            A list of tuples in the form of (SYSTEM_PATH, RELATIVE_PATH).
        """
        file_locations = []
        filenames = []
        for module_path in self.__found_module_paths:
            if self.__module_in_full_packages(module_path):
                continue

            module = utils.import_module(module_path)
            try:
                module_filename = module.__file__
            except AttributeError:
                continue

            # Ignore `.jar` files and in case `module_filename` is None
            # TODO (olliwang): Support adding `.jar` files automatically
            if not module_filename or module_filename.endswith('.jar'):
                continue

            # For Jython: Fix filename if starts with `__pyclasspath__`
            if module_filename.startswith('__pyclasspath__'):
                module_filename = module_filename.replace('__pyclasspath__',
                                                          self.basedir)
                if not os.path.isfile(module_filename):
                    module_filename = None

            if module_filename:
                filenames.append(module_filename)

        # Get all available filenames under a package
        for package_name in self.__full_packages:
            module = utils.import_module(package_name)
            package_dir = os.path.dirname(module.__file__)
            # For Jython: Fix path if starts with `__pyclasspath__`
            if package_dir.startswith('__pyclasspath__'):
                package_dir = package_dir.replace('__pyclasspath__',
                                                  self.basedir)
            if os.path.dirname(package_dir) not in self.sys_path:
                continue
            for filename in utils.iter_dir_filenames(package_dir):
                root, ext = os.path.splitext(filename)
                # Keep only source module if possible
                for ext in self.invalid_exts:
                    # Filter invalid compiled python module
                    if filename.endswith(ext):
                        break
                else:
                    # Compile source modules
                    if compile_all or filename.startswith(self.basedir):
                        filename = utils.compile_py(filename,
                                                    self.compiled_ext)
                    # Do not compile module if compiled module exists
                    else:
                        if filename.endswith('.py'):
                            root, ext = os.path.splitext(filename)
                            compiled_filename = root + self.compiled_ext
                            if os.path.isfile(compiled_filename):
                                filename = None
                            else:
                                filename = utils.compile_py(filename,
                                                            self.compiled_ext)
                    if filename and filename not in filenames:
                        filenames.append(filename)

        # Separate module_filename to system path and the rest
        for filename in filenames:
            for sys_path in self.sys_path:
                if not filename.startswith(sys_path):
                    continue
                # Remove syspath from filename
                filename = filename.split(sys_path + os.path.sep, 1)[1]
                location = (sys_path, filename)
                if location not in file_locations:
                    file_locations.append(location)
                break
        return file_locations

    def copy_to(self, destdir, compile_all=False):
        """Copy dependent files to specified directory.

        Args:
            destdir: The directory path containing copied files.
            compile_all: Whether to compile all Python modules.

        Returns:
            The count number of copied files.
        """
        egg_cache = {}
        count = 0
        for sys_path, relative_path in self.get_file_locations(compile_all):
            count += 1
            dest_path = os.path.join(destdir, relative_path)
            # Copy the file within an egg file
            if zipfile.is_zipfile(sys_path):
                if sys_path in egg_cache:
                    egg = egg_cache[sys_path]
                else:
                    egg = zipfile.ZipFile(sys_path)
                    egg_cache[sys_path] = egg
                f = open(dest_path, 'wb')
                try:
                    f.write(egg.read(relative_path))
                finally:
                    f.close()
            # Copy the file from a directory
            else:
                src_path = os.path.join(sys_path, relative_path)
                dest_dirname = os.path.dirname(dest_path)
                if not os.path.isdir(dest_dirname):
                    os.makedirs(dest_dirname)
                shutil.copy2(src_path, dest_path)
        return count

