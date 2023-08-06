#!/usr/bin/python
from __future__ import with_statement

import sys; sys.path.append('.')

from contextlib import nested
import os.path
from shutil import copy
from subprocess import call

from colorworld import make_map

from testutils import ConsistencyTestCase
from unittest import main, TestCase

def read(filename):
    with file(filename) as stream:
        return stream.read()


def ensure_dir(direc):
    if not os.path.isdir(direc):
        os.mkdir(direc)


class Test(ConsistencyTestCase):
    def setUp(self):
        self.old_cwd = os.getcwd()
        os.chdir('temp')

    def tearDown(self):
        os.chdir(self.old_cwd)


    def test_stdin(self):
        streams = nested(file('../testdata/test.csv', 'r'),
                         file('from_stdout.svg', 'w'))
        with streams as (in_stream, out_stream):
            call("../color-world.py", stdin=in_stream, stdout=out_stream)
        self.assertConsistent("from_stdout.svg", stored_file="default.svg")


    def test_stdin_with_output(self):
        with file('../testdata/test.csv', 'r') as in_stream:
            call("../color-world.py -o stdin_to_file.svg".split(), 
                 stdin=in_stream)
        self.assertConsistent("stdin_to_file.svg", stored_file="default.svg")


    def test_run_on_file(self):
        copy('../testdata/test.csv', '.')
        call("../color-world.py test.csv".split())
        self.assertConsistent("test.svg", stored_file="default.svg")


    def test_run_on_file_with_output(self):
        copy('../testdata/test.csv', '.')
        call("../color-world.py -o specified.svg test.csv".split())
        self.assertConsistent("specified.svg", stored_file="default.svg")


    def test_other_options(self):
        copy('../testdata/test.csv', '.')
        call("../color-world.py -H 300 -d 20 -u joules -m -2 -o most-options.svg test.csv".split())
        self.assertConsistent("most-options.svg")


    def test_long_names(self):
        copy('../testdata/longnames.csv', '.')
        call("../color-world.py -l longnames.csv".split())
        self.assertConsistent("longnames.svg")


    def test_survives_pathologies(self):
        copy('../testdata/whitespace.csv', '.')
        ret = call('../color-world.py whitespace.csv'.split())
        self.assertEquals(ret, 0)
        self.assertConsistent('whitespace.svg', stored_file='default.svg')


    def test_different_directories(self):
        ensure_dir("different_directory")
        copy('../testdata/test.csv', 'different_directory')
        call('../color-world.py different_directory/test.csv'.split())
        self.assertConsistent('different_directory/test.svg', stored_file='default.svg')

        
    def test_different_directories_local_output(self):
        ensure_dir("different_directory")
        copy('../testdata/test.csv', 'different_directory')
        call('../color-world.py different_directory/test.csv -o local_output.svg'.split())
        self.assertConsistent('local_output.svg', stored_file='default.svg')
        

if __name__ == "__main__":
    main()


