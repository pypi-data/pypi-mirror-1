# Copyright (c) 2008 gocept gmbh & co. kg
# See also LICENSE.txt

import distutils.ccompiler
import re
import os
import os.path
import shutil
import stat
import subprocess
import sys
import tempfile


class CxOracle(object):

    client_library_pattern = re.compile(
        r'^(libclntsh)\.([[a-z]+)\.([\d.]+)$')

    def __init__(self, buildout, name, options):
        self.buildout = buildout
        self.name = name
        self.options = options
        self.part_directory = options['oracle-home'] = os.path.join(
            buildout['buildout']['parts-directory'],
            name)
        options.setdefault('loader-name', name)
        self.loader = options['_loader_path'] = os.path.join(
            buildout['buildout']['bin-directory'], options['loader-name'])
        options['executable'] = self.loader

    def install(self):
        if os.path.isdir(self.part_directory):
            shutil.rmtree(self.part_directory)
        os.mkdir(self.part_directory)
        self.prepare_oracle_home()
        self.create_loader()
        return self.part_directory, self.loader

    def update(self):
        pass

    def prepare_oracle_home(self):
        """Prepare the part directory to contain all the libraries required."""
        self.unzip(self.options['instant-client'])
        self.unzip(self.options['instant-sdk'])

        symlink_source = None
        for filename in os.listdir(self.part_directory):
            m = self.client_library_pattern.match(filename)
            if m is not None:
                library_base_name = m.group(1)
                library_kind = m.group(2)
                version = m.group(3)
                symlink_source = filename
                break
        if symlink_source is None:
            raise Exception('Could not find libclntsh.')

        symlink_target = '%s.%s' % (library_base_name, library_kind)
        os.symlink(os.path.join(self.part_directory, symlink_source),
                   os.path.join(self.part_directory, symlink_target))

    def create_loader(self):
        old_cwd = os.getcwd()
        work_dir = tempfile.mkdtemp()
        try:
            os.chdir(work_dir)
            shutil.copy(os.path.join(os.path.dirname(__file__), 'loader.c'),
                        os.path.join(work_dir, 'loader.c'))

            compiler = distutils.ccompiler.new_compiler()
            compiler.define_macro('PYTHON_EXECUTABLE',
                                  '"%s"' % sys.executable)
            compiler.define_macro('ORACLE_HOME',
                                  '"%s"' % self.options['oracle-home'])

            compiler.compile(['loader.c'])
            compiler.link_executable(['loader.o'], self.options['loader-name'])
            shutil.move(os.path.join(work_dir, self.options['loader-name']),
                        self.loader)
        finally:
            os.chdir(old_cwd)
            shutil.rmtree(work_dir)


    def unzip(self, filename):
        """Helper to unzip an archive to the parts directory."""
        extract_dir = tempfile.mkdtemp()
        try:

            call = subprocess.Popen(
                ['unzip', filename, '-d', extract_dir],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            stdout, stderr = call.communicate()

            if call.returncode != 0:
                raise Exception('Extraction of file %r failed.' % filename)

            contents = os.listdir(extract_dir)
            assert len(contents) == 1
            root = os.path.join(extract_dir, contents[0])
            for filename in os.listdir(root):
                shutil.move(os.path.join(root, filename),
                            os.path.join(self.part_directory, filename))
        finally:
            shutil.rmtree(extract_dir)
