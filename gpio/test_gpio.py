#!/usr/bin/env python3

import cffi
import unittest
import sys
import os
import uuid
import subprocess
import importlib
import glob
import shutil
import re

from pycparser import c_ast, CParser, c_generator
from unittest import mock

def preprocess(source):
    return subprocess.run(['gcc', '-E', '-P', '-'],
                          input=source, stdout=subprocess.PIPE,
                          universal_newlines=True, check=True).stdout


def convert_function_declarations(source, blacklist):
    return CFFIGenerator(blacklist).visit(CParser().parse(source))


class FunctionList(c_ast.NodeVisitor):
    def __init__(self, source):
        self.funcs = set()
        self.visit(CParser().parse(source))
        
    def visit_FuncDef(self, node):
        self.funcs.add(node.decl.name)


class CFFIGenerator(c_generator.CGenerator):
    def __init__(self, blacklist):
        super().__init__()
        self.blacklist = blacklist
        
    def visit_Decl(self, n, *args, **kwargs):
        result = super().visit_Decl(n, *args, **kwargs)
        if isinstance(n.type, c_ast.FuncDecl):
            if n.name not in self.blacklist:
                return 'extern "Python+C" ' + result
        return result

def load(path, filename):
    name = filename + '_' + uuid.uuid4().hex

    source = open(path + '/' + filename + '.c').read()
    # preprocess all header files for CFFI
    includes = ""
    headers = ''.join(re.findall('\s*#include\s+.*', source))
    headers = headers.split('\n')
    
    # get headers name without #include
    for header in headers:
        spos = header.find('\"') + 1
        epos = header.find('\"', spos + 1)
        includes += preprocess(open(header[spos:epos]).read())
    # prefix external functions with extern "Python+C"
    local_functions = FunctionList(preprocess(source)).funcs
    includes = convert_function_declarations(includes, local_functions)

    ffibuilder = cffi.FFI()
    ffibuilder.cdef(includes)
    ffibuilder.set_source(name, source)
    ffibuilder.compile()

    module = importlib.import_module(name)
    # return both the library object and the ffi object
    return name, module.lib, module.ffi

class GPIOTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fin = 'gpio'
        cls.name, cls.lib, cls.ffi = load(os.getcwd() + '/' + cls.fin, cls.fin)
    
    @classmethod
    def tearDownClass(cls):
        # remove all meta files after tests
        py_cache_file = os.getcwd() + '/' + cls.fin + '/' + '__pycache__'
        shutil.rmtree(py_cache_file)
        for f in glob.glob(cls.name + '.*'):
            os.remove(f)

    def test_read_gpio0(self):
        @self.ffi.def_extern()
        def read_gpio0():
            return 42
        
        self.assertEqual(self.lib.read_gpio(0), 42)

    def test_read_gpio1(self):
        read_gpio1 = unittest.mock.MagicMock(return_value=21)
        self.ffi.def_extern('read_gpio1')(read_gpio1)
        self.assertEqual(self.lib.read_gpio(1), 21)
        read_gpio1.assert_called_once_with()

if __name__ == "__main__":
    unittest.main()
