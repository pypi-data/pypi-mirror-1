from __future__ import with_statement

import os.path

from unittest import TestCase

def read(filename):
    with file(filename) as stream:
        return stream.read()


class ConsistencyTestCase(TestCase):

    def assertConsistent(self, filename, stored_file=None):
        stored_file = stored_file or filename
        self.assertEquals(read(filename), 
                    read(os.path.join('../consistency', stored_file)),
                    "%s differs from the stored version" % filename)

