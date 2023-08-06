from __future__ import with_statement
import sys; sys.path.append('.')
from colorworld import make_map
from testutils import ConsistencyTestCase

from unittest import main
import os.path

def read(filename):
    with file(filename) as stream:
        return stream.read()

class Test(ConsistencyTestCase):
    def setUp(self):
        self.old_cwd = os.getcwd()
        os.chdir('temp')

    def tearDown(self):
        os.chdir(self.old_cwd)


    def test_from_file(self):
        make_map('../testdata/test.csv', 'from_file.svg')
        self.assertConsistent('from_file.svg', stored_file='default.svg')


    def test_from_dict(self):
        from csv import reader
        with file('../testdata/test.csv') as f:
            data = dict((x[0], float(x[1])) for x in reader(f) if len(x) == 2)

        make_map(data, 'from_dict.svg')
        self.assertConsistent('from_dict.svg', stored_file='default.svg')


    def test_basic(self):
        make_map(file('../testdata/test.csv', 'r'), 'basic.svg')
        self.assertConsistent('basic.svg', stored_file='default.svg')


    def test_with_options(self):
        make_map(file('../testdata/test.csv', 'r'), 'divisions.svg', divisions=10)
        self.assertConsistent('divisions.svg')


    def test_with_options_units(self):
        make_map(file('../testdata/test.csv', 'r'), 'units.svg', unit='flees')
        self.assertConsistent('units.svg')


    def test_invalid_options(self):
        self.assertRaises(TypeError, make_map, None, None, unknown=None)


if __name__ == "__main__":
    main()


