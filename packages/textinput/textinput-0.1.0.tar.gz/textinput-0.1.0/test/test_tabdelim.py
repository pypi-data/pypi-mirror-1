#!/usr/bin/env python

__version__ = "$Revision: 1.1 $"

import unittest

import tabdelim

class TestDictReader(unittest.TestCase):
    def test_tabified(self):
        lines =['JOBID\tARRAY_SPEC',
                '266915\ti.blastz.mbe[1-1000]%200']
        reader = tabdelim.DictReader(lines)
        jobinfo = reader.next()
        self.assertEqual(jobinfo["ARRAY_SPEC"], "i.blastz.mbe[1-1000]%200")

        reader = tabdelim.DictReader(lines, skipinitialspace=True)
        jobinfo = reader.next()
        self.assertEqual(jobinfo["ARRAY_SPEC"], "i.blastz.mbe[1-1000]%200")

    def test_untabified(self):
        lines =['JOBID    ARRAY_SPEC',
                '266915   i.blastz.mbe[1-1000]%200']
        reader = tabdelim.DictReader(lines, delimiter=" ", skipinitialspace=True)
        jobinfo = reader.next()
        self.assertEqual(jobinfo["ARRAY_SPEC"], "i.blastz.mbe[1-1000]%200")

if __name__ == "__main__":
    unittest.main()
