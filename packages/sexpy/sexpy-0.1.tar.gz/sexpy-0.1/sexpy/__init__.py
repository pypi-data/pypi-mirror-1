# Copyright 2007 Ero-sennin
#
# This file is part of SEXpy.
#
# SEXpy is free software; you can redistribute it and/or modify
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 2 of the License, or (at your
# option) any later version.
#
# SEXpy is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with pybtex; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301
# USA

import sys
import imp
import struct
import time
import marshal
from os import path

from sexpy.translator import compile
from sexpy.parser import parse, String, List
from sexpy.toplevel import toplevel


__version__='0.1'

def parse_file(filename):
    return parse(file(filename), filename)

def compile_file(filename):
    sex_ast = parse_file(filename)
    code = compile(sex_ast, filename)
    pyc_filename = path.extsep.join([path.splitext(filename)[0], 'pyc'])
    pyc_file = file(pyc_filename, 'wb')
    pyc_file.write(imp.get_magic())
    pyc_file.write(struct.pack('<l', time.time()))
    marshal.dump(code, pyc_file)
    pyc_file.close()

def import_file(filename, name=None):
    sex_ast = parse_file(filename)
    code = compile(sex_ast, filename)
    if name is None:
        name = path.splitext(filename)[0]
    module = imp.new_module(name)
    exec code in module.__dict__
    sys.modules[name] = module
    return module

def run_file(filename):
    import_file(filename, '__main__')
