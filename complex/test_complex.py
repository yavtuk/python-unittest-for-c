#!/usr/bin/env python3

import cffi
import unittest
import sys
import os
import uuid
import subprocess
import importlib
import ctypes
import glob
import shutil

class complex_t(ctypes.Structure):
    _fields_ = [("re", ctypes.c_uint32), 
                ("im", ctypes.c_uint32)]
    
    def __init__(self, re, im):
        self.re = re
        self.im = im

def preprocess(source):
    return subprocess.run(['gcc', '-E', '-P', '-'],
                          input=source, stdout=subprocess.PIPE,
                          universal_newlines=True, check=True).stdout
                          

class AddTest(unittest.TestCase):
    def setUp(self):
        self.fin = 'complex'
        self.etalon = complex_t(6, 6)

    def load(self, path, filename):
        self.name = filename + '_' + uuid.uuid4().hex

        source = open(path + '/' + filename + '.c').read()
        # handle preprocessor directives
        includes = preprocess(open(path + '/' + filename + '.h').read())

        ffibuilder = cffi.FFI()
        ffibuilder.cdef(includes)
        ffibuilder.set_source(self.name, source, libraries=[])
        ffibuilder.compile(verbose=True)
        module = importlib.import_module(self.name)
        return [module.lib, module.ffi]

    def test_addition(self):
        fin = 'complex'
        [module, ffi] = self.load(os.getcwd() + '/' + fin + '/', fin)
        lhs = ffi.new('complex_t *', (2, 3))
        rhs = ffi.new('complex_t *', (4, 3))
        res = module.summ(lhs, rhs)
        self.assertEqual(res.re, self.etalon.re)
        self.assertEqual(res.im, self.etalon.im)

    def tearDown(self):
        py_cache_file = os.getcwd() + '/' + self.fin + '/' + '__pycache__'
        shutil.rmtree(py_cache_file)
        for f in glob.glob(self.name + '.*'):
            os.remove(f)

if __name__ == "__main__":
    unittest.main()

