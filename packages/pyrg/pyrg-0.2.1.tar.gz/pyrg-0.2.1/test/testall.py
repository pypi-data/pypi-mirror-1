import unittest
import sys
import os
sys.path.insert(0, os.path.abspath("pyrg"))
import pyrg


class ColorFunctionTest(unittest.TestCase):

    def test_coloring_method(self):
        line = "get_gg (__main__.TestTest)"
        self.assertEqual("[36mget_gg (__main__.TestTest)[0m",
                         pyrg.coloring_method(line))

    def test_ngroute(self):
        pass
        input_strings = """..
----------------------------------------------------------------------
Ran 2 tests in 0.000s

OK
"""
        result_strings = """[32m.[0m[32m.[0m
----------------------------------------------------------------------
Ran 2 tests in 0.000s

[32mOK[0m"""
        ret = pyrg.parse_unittest_result(input_strings.splitlines(1))
        self.assertEqual(ret, result_strings)


if __name__ == '__main__':
    unittest.main()
