#!/usr/bin/env python
"""test_pyprof2html - testing script for pyprof2html

require pikzie module(http://pikzie.sourceforge.net/)
"""

import sys
sys.path.insert(0, './pyprof2html')     ## test to development path
import pyprof2html as p2h

# warning handling
# 'The popen2 module is deprecated.  Use the subprocess module.'
import warnings
warnings.filterwarnings('ignore', category=DeprecationWarning,
                        message=r'The popen2 module is deprecated.')
import pikzie


class TestFileTypeCheck(pikzie.TestCase):

    def test_hotshot(self):
        self.assert_equal(True,
                p2h.check_hotshot("jifejihotshot-versionfijeifje)"))

    def test_nothotshot(self):
        self.assert_equal(False, p2h.check_hotshot("jotionfijeifje"))


class TestConvertUnit(pikzie.TestCase):

    def test_millisec1(self):
        ret = p2h.convert_unit(0.01)
        self.assert_equal(ret, "10.0 [ms]")

    def test_millisec100(self):
        ret = p2h.convert_unit(0.005)
        self.assert_equal(ret, "5.0 [ms]")

    def test_microsec1(self):
        ret = p2h.convert_unit(0.0009)
        self.assert_equal(ret, "900.0 [us]")

    def test_microsec100(self):
        ret = p2h.convert_unit(0.000009)
        self.assert_equal(ret, "9.0 [us]")

    def test_notconvert(self):
        ret = p2h.convert_unit(1.008009)
        self.assert_equal(ret, "1.008 [ s]")

    def test_nanosec1(self):
        ret = p2h.convert_unit(0.000000008)
        self.assert_equal(ret, "8.0 [ns]")


hotshotline_testdata_path = './test/hotshot.prof'
hotshot_testdata_path = './test/hot.prof'
cprof_testdata_path = './test/cprof.prof'


class TestExecute(pikzie.TestCase):

    def setup(self):
        self.defaultstdout = sys.stdout
        sys.stdout = open('/dev/null', 'w')

    def teardown(self):
        sys.stdout = self.defaultstdout

    def test_cprofraw(self):
        prof = p2h.Converter(cprof_testdata_path)
        prof.printout('raw')
        self.assert_equal(True, True)

    def test_cprofhtml(self):
        prof = p2h.Converter(cprof_testdata_path)
        prof.printout('html')
        self.assert_equal(True, True)

    def test_hotshotraw(self):
        prof = p2h.Converter(hotshot_testdata_path)
        prof.printout('raw')
        self.assert_equal(True, True)

    def test_hotshothtml(self):
        prof = p2h.Converter(hotshot_testdata_path)
        prof.printout('html')
        self.assert_equal(True, True)

    def test_hotshotlinehtml(self):
        prof = p2h.Converter(hotshotline_testdata_path)
        prof.printout('html')
        self.assert_equal(True, True)


class ColorMappingTest(pikzie.TestCase):

    def test_mapping_v1(self):
        ret = p2h.mapping_table(1, 1000)
        self.assert_equal(ret, '#ccffcc')

    def test_mapping_v2(self):
        ret = p2h.mapping_table(29, 1000)
        self.assert_equal(ret, '#66ff99')

    def test_mapping_v3(self):
        ret = p2h.mapping_table(79, 1000)
        self.assert_equal(ret, '#ffcc33')

    def test_mapping_v4(self):
        ret = p2h.mapping_table(119, 1000)
        self.assert_equal(ret, '#ff6666')

    def test_mapping_v5(self):
        ret = p2h.mapping_table(199, 1000)
        self.assert_equal(ret, '#ff3333')

    def test_mapping_min(self):
        ret = p2h.mapping_table(0, 100)
        self.assert_equal(ret, '#ccffcc')

    def test_mapping_max(self):
        ret = p2h.mapping_table(100, 100)
        self.assert_equal(ret, '#ff3333')

    def test_mapping_v1_float(self):
        ret = p2h.mapping_table(1., 1000.)
        self.assert_equal(ret, '#ccffcc')

    def test_mapping_v2_float(self):
        ret = p2h.mapping_table(10., 1000.)
        self.assert_equal(ret, '#66ff99')

    def test_mapping_v3_float(self):
        ret = p2h.mapping_table(79., 1000.)
        self.assert_equal(ret, '#ffcc33')

    def test_mapping_v4_float(self):
        ret = p2h.mapping_table(119., 1000.)
        self.assert_equal(ret, '#ff6666')

    def test_mapping_v5_float(self):
        ret = p2h.mapping_table(199., 1000.)
        self.assert_equal(ret, '#ff3333')

    def test_mapping_min_float(self):
        ret = p2h.mapping_table(0.0, 1000.0)
        self.assert_equal(ret, '#ccffcc')

    def test_mapping_max_float(self):
        ret = p2h.mapping_table(100., 100.)
        self.assert_equal(ret, '#ff3333')


class FindFileCodec(pikzie.TestCase):

    def test_emacs_style1_eucjp(self):
        ret = p2h.detect_filecodec(["# -*- coding=euc-jp -*-"])
        self.assert_equal(ret, 'euc-jp')

    def test_emacs_style1(self):
        ret = p2h.detect_filecodec(["# -*- coding=utf-8 -*-"])
        self.assert_equal(ret, 'utf-8')

    def test_vim_style1(self):
        ret = p2h.detect_filecodec(["# vim: fileencoding=utf-8"])
        self.assert_equal(ret, 'utf-8')

    def test_vim_style1_shiftjis(self):
        ret = p2h.detect_filecodec(["# vim: fileencoding=shift_jis"])
        self.assert_equal(ret, 'shift_jis')
