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

def preprocess(source):
    return subprocess.run(['gcc', '-E', '-P', '-'],
                          input=source, stdout=subprocess.PIPE,
                          universal_newlines=True, check=True).stdout
                          
class AddTest(unittest.TestCase):
    def setUp(self):
        self.fin = 'add'

    def load(self, path, filename):
        self.name = filename + '_' + uuid.uuid4().hex

        source = open(path + '/' + filename + '.c').read()
        # handle preprocessor directives
        includes = preprocess(open(path + '/' + filename + '.h').read())
        
        ffibuilder = cffi.FFI()
        ffibuilder.cdef(includes)
        ffibuilder.set_source(self.name, source)
        ffibuilder.compile()

        module = importlib.import_module(self.name)
        return module.lib

    def test_addition(self):
        module = self.load(os.getcwd() + '/' + self.fin, self.fin)
        self.assertEqual(module.add(1, 2), 1 + 2)

    def tearDown(self):
        py_cache_file = os.getcwd() + '/' + self.fin + '/' + '__pycache__'
        shutil.rmtree(py_cache_file)
        for f in glob.glob(self.name + '.*'):
            os.remove(f)

if __name__ == "__main__":
    unittest.main()

