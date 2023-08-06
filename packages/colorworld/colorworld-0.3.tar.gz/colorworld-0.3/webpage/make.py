#!/usr/bin/python
from __future__ import with_statement
from Cheetah.Template import Template

import sys; sys.path.append('..')
from colorworld import make_map
from subprocess import Popen, PIPE

libdoc = make_map.__doc__
exedoc = Popen(["../color-world.py", "--help"], stdout=PIPE).communicate()[0]
with file('index.html', 'w') as f:
    f.write(str(Template(file='index.tmpl', namespaces=[locals(), globals()])))
