#!/usr/bin/env python
"""test_pyprof2html - testing script for pyprof2html

require pikzie module(http://pikzie.sourceforge.net/)
"""

import sys
import pyprof2html as pyhtml

# warning handling
# 'The popen2 module is deprecated.  Use the subprocess module.'
import warnings  
warnings.filterwarnings('ignore', category=DeprecationWarning,
                        message=r'The popen2 module is deprecated.')
import pikzie

class TestFileTypeCheck(pikzie.TestCase):

    def test_hotshot(self):
        self.assert_equal(True, pyhtml.check_hotshot("jifejihotshot-versionfijeifje)"))

    def test_nothotshot(self):
        self.assert_equal(False, pyhtml.check_hotshot("jotionfijeifje"))


hotshotline_testdata_path = './test/hotshot.prof'
hotshot_testdata_path = './test/hot.prof'
cprof_testdata_path   = './test/cprof.prof'

class TestExecute(pikzie.TestCase):

    def setup(self):
        self.defaultstdout = sys.stdout
        sys.stdout = open('/dev/null', 'w')

    def teardown(self):
        sys.stdout = self.defaultstdout

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

    def test_hotshotlinehtml(self):
        prof = pyhtml.Converter(hotshotline_testdata_path)
        prof.printout('html')
        self.assert_equal(True, True)


