#!/usr/bin/env python
"""test_pyprof2html - testing script for pyprof2html

require pikzie module(http://pikzie.sourceforge.net/)
"""
import sys
import pikzie
import pyprof2html as pyhtml


class TestFileTypeCheck(pikzie.TestCase):

    def test_hotshot(self):
        self.assert_equal(True, pyhtml.check_hotshot("jifejihotshot-versionfijeifje)"))

    def test_nothotshot(self):
        self.assert_equal(False, pyhtml.check_hotshot("jotionfijeifje"))


hotshot_testdata_path = './test/hotshot.prof'
cprof_testdata_path   = './test/cprof.prof'
sys.stdout = open('/dev/null', 'w')

class TestExecute(pikzie.TestCase):

    def test_cprofraw(self):
        prof = pyhtml.Converter(cprof_testdata_path)
        prof.printout('raw')
        self.assert_equal(True, True)

    def test_cprofhtml(self):
        prof = pyhtml.Converter(cprof_testdata_path)
        prof.printout('html')
        self.assert_equal(True, True)

    def test_hotshotraw(self):
        prof = pyhtml.Converter(hotshot_testdata_path)
        prof.printout('raw')
        self.assert_equal(True, True)

    def test_hotshothtml(self):
        prof = pyhtml.Converter(hotshot_testdata_path)
        prof.printout('html')
        self.assert_equal(True, True)

