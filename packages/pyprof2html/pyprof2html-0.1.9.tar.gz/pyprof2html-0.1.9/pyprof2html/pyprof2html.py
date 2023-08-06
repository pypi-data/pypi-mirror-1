# -*- coding: utf-8 -*-
"""pyprof2html - Profile data convert to HTML.

This script is converted to HTML file from Python's cProfile and
hotshot profiling data.
"""

import codecs
import os
import re
import sys
import time
from hotshot import log, stats
from pstats import Stats

from jinja2 import Environment, PackageLoader

__version__ = '0.1.9'
__licence__ = 'New BSD License'
__author__ = 'Hideo Hattori <hhatto.jp@gmail.com>'

__all__ = ['Converter']

ENVIRON = Environment(loader=PackageLoader('pyprof2html',
                      './templates', encoding='utf-8'))


def check_hotlinetimings(dump):
    """check to linetimings hotshot-profile datafile."""
    signature = "yes"
    return signature in dump


def check_hotshot(dump):
    """check to hotshot-profile datafile."""
    signature = "hotshot-version"
    return signature in dump


def mapping_table(target, nall):
    levelmap = {0: '#ccffcc',   # yellow green (light)
                1: '#66ff99',   # yellow green
                2: '#ffcc33',   # orange
                3: '#ff6666',   # pink
                4: '#ff3333',   # red
                }
    levels = [nall * 0.01, nall * 0.03, nall * 0.08, nall * 0.12, nall * 0.20]
    for level in range(len(levels)):
        if target < levels[level]:
            return levelmap[level]
    return levelmap[len(levelmap) - 1]


def detect_filecodec(lines):
    """detect to Python Source Code Encodings.

    Only strict check. see PEP 0263...
    """
    re_codec = re.compile("coding[:=]\s*([-\w.]+)")
    for cnt, line in enumerate(lines):
        if re_codec.search(line):
            return re_codec.findall(line)[0]
        if cnt >= 2:
            break
    return None


def convert_unit(float_number):
    """convert to unit of profile data.

    >>> convert_unit(0.12345)
    '123.5 [ms]'
    >>> convert_unit(0.12385)
    '123.9 [ms]'
    >>> convert_unit(0.12395)
    '124.0 [ms]'
    >>> convert_unit(0.0012395)
    '1.2 [ms]'
    >>> convert_unit(0.000012395)
    '12.4 [us]'
    >>> convert_unit(5)
    '5.000 [ s]'
    >>> convert_unit(5.9)
    '5.900 [ s]'
    >>> convert_unit(5.91)
    '5.910 [ s]'
    """
    if 1 > float_number >= 0.001:
        float_number = "%3.1lf [ms]" % (float_number * 1000)
    elif 0.001 > float_number >= 0.000001:
        float_number = "%3.1lf [us]" % (float_number * 1000000)
    elif 0.000001 > float_number >= 0.000000001:
        float_number = "%3.1lf [ns]" % (float_number * 1000000000)
    else:
        float_number = "%1.3lf [ s]" % float_number
    return float_number


def create_stylefile(output_directory):
    """create to ./style.css and jquery.js file"""
    for filename in ('style.css', 'jquery.js', 'jquery.tablesorter.js'):
        fp = open('./%s/%s' % (output_directory, filename), 'w')
        print >> fp, ENVIRON.get_template(filename).render()
        fp.close()


class Converter(object):
    """output to HTML from profile data
    """

    def __init__(self, filename):
        self.outfile = None
        self.output_dir = 'html'
        self.output_htmlfile = 'index.html'
        dump = open(filename).read()
        if check_hotshot(dump[:20]):
            self.prof = stats.load(filename)
            self.tmpl = ENVIRON.get_template('basic.html')
            self.profile_datatype = "hotshot"
            if check_hotlinetimings(dump[102:108]):
                self.profline = log.LogReader(filename)
                self.tmplline = ENVIRON.get_template('hotshot-line.html')
                self.profile_datatype = "hotshot(line)"
        else:
            self.prof = Stats(filename)
            self.tmpl = ENVIRON.get_template('basic.html')
            self.profile_datatype = "cProfile"
        self.filename = filename
        self.proftime = time.ctime(os.stat(filename).st_mtime)
        self.reporttime = time.ctime()
        self.outputtype = 'html'
        self.functions_number = 20

    def _printhtml_source(self, filename, profs, outputfile):
        """printing one file profile line. return value is html render
        strings.
        """
        result = []
        if not os.path.exists(filename):
            return ""
        filecodec = detect_filecodec(open(filename).readlines())
        if filecodec is None:
            fileobj = open(filename)
        else:
            fileobj = codecs.open(filename, 'r', filecodec)
        for num, line in enumerate(fileobj, 1):
            if num in profs:
                result.append({'sec': profs[num]['sec'],
                               'cnt': profs[num]['cnt'],
                               'line': line})
            else:
                result.append({'sec': 'None', 'line': line})
        titletext = "pyprof2html - %s" % filename
        renderdict = {'title': titletext,
                      'proftime': self.proftime,
                      'reporttime': self.reporttime,
                      'filename': filename,
                      'profile_datatype': self.profile_datatype,
                      'version': __version__,
                      'profdata': {'data': result,
                                   'totaltime': "%8.4lf" % self.prof.total_tt,
                                   'totalcalls': self.prof.total_calls}}
        if filecodec is None:
            print >> outputfile, self.tmplline.render(renderdict)
        else:
            self.tmplline.stream(renderdict).dump(outputfile, 'utf-8')

    def _print_source(self, filename, profs):
        """printing one file profile line. return value is text strings.
        """
        result = []
        if not os.path.exists(filename):
            return ""
        result.append("=" * 60 + "\n")
        result.append(filename + "\n")
        result.append("=" * 60 + "\n")
        for num, line in enumerate(open(filename).readlines(), 1):
            if num in profs:
                result.append(" %3.4lfs | %7dn | %s" % (profs[num]['sec'],
                                                        profs[num]['cnt'],
                                                        line))
            else:
                result.append("         |          | %s" % (line))
        return ''.join(result)

    def _print_sources(self, profs):
        """wrapper of _print_source() and _printhtml_source() method.
        """
        ret = []
        sources = []
        info = {}
        filecnt = 0
        for i, prof in enumerate(profs):
            filename = prof[0]
            if (not sources.count(filename)) or (len(profs) == (i + 1)):
                if info != {}:
                    if self.outputtype == 'html':
                        out_filename = "%s/%s.html" % (self.output_dir,
                                       sources[filecnt].replace('/', '_'))
                        outputfile = open(out_filename, 'w')
                        self._printhtml_source(sources[filecnt],
                                               info, outputfile)
                        outputfile.close()
                    else:
                        ret.append(self._print_source(sources[filecnt], info))
                    filecnt += 1
                info = {}
                sources.append(filename)
            info[prof[1]] = {'sec': prof[2], 'cnt': prof[3]}
        return "".join(ret)

    def _analyze_profline(self):
        """analyzed to hotshot linetimings data.
        """
        profset = dict()
        for i in self.profline:
            if i[0] == 0 or i[0] == 1:  # WHAT_ENTER or WHAT_EXIT
                continue
            if i[1] not in profset:
                profset[i[1]] = [float(int(i[2]) / 1000000.), i[2]]
            else:
                profset[i[1]][0] += float(int(i[2]) / 1000000.)
                profset[i[1]][1] += i[2]
        profs = [(p[0], p[1], profset[p][0], profset[p][1]) for p in profset]
        profs.sort()
        return profs

    def _analyzed_prof(self):
        """analyzed to not linetimings profile data.
        """
        self.prof.sort_stats('time', 'calls')
        self.prof.stream = open(os.devnull, 'w')    # darty hack
        backstream = self.prof.stream
        tmp, funclist = self.prof.get_print_list(())
        self.prof.stream = backstream
        self.prof.stream.close()
        datalist = list()
        cnt = 0
        for func in funclist:
            if cnt >= self.functions_number:
                break
            cnt += 1
            stat = self.prof.stats[func]
            ncalls = stat[0]
            if not int(ncalls):
                ## skip to 0calls function
                continue
            #tottime = convert_unit(stat[2])
            tottime = "%8.4lf" % stat[2]
            try:
                totpercall = "%8.4lf" % float(stat[2] / stat[0])
            except ZeroDivisionError:
                totpercall = "0.0000"
            cumtime = "%8.4lf" % stat[3]
            try:
                cumpercall = "%8.4lf" % float(stat[3] / stat[0])
            except ZeroDivisionError:
                cumpercall = "0.0000"
            ncallslevel = mapping_table(ncalls, self.prof.total_calls)
            tottlevel = mapping_table(stat[2], self.prof.total_tt)
            totclevel = mapping_table(float(totpercall), self.prof.total_tt)
            cumtlevel = mapping_table(1, 1000)
            cumclevel = mapping_table(1, 1000)
            linelink = "%s.html" % func[0].replace('/', '_')
            data = {
                'func': func,
                'linelink': linelink,
                'ncalls': ncalls,
                'tottime': tottime,
                'cumtime': cumtime,
                'totpercall': totpercall,
                'cumpercall': cumpercall,
                'ncallslevel': ncallslevel,
                'cumtimelevel': cumtlevel,
                'tottimelevel': tottlevel,
                'totcalllevel': totclevel,
                'cumcalllevel': cumclevel,
            }
            datalist.append(data)
        profdata = {
            'totaltime': "%8.4lf" % self.prof.total_tt,
            'totalcalls': self.prof.total_calls,
            'data': datalist,
        }
        return profdata

    def _hookraw(self):
        """hook rawtext print
        """
        if self.profile_datatype == 'hotshot(line)':
            profs = self._analyze_profline()
            print self._print_sources(profs)
        else:
            self.prof.sort_stats('time', 'calls')
            self.prof.print_stats()

    def _hookhtml(self):
        """hook html print
        """
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        filepath = "%s/%s" % (self.output_dir, self.output_htmlfile)
        self.outfile = open(filepath, 'w')
        profdata = self._analyzed_prof()
        titletext = "pyprof2html - %s" % self.filename
        create_stylefile(self.output_dir)
        if self.profile_datatype == 'hotshot(line)':
            profs = self._analyze_profline()
            self._print_sources(profs)
        print >> self.outfile, \
                 self.tmpl.render(title=titletext,
                                  proftime=self.proftime,
                                  reporttime=self.reporttime,
                                  profdata=profdata,
                                  thisname=self.output_htmlfile,
                                  version=__version__,
                                  profile_datatype=self.profile_datatype)
        self.outfile.close()

    def printout(self, filetype='html'):
        """print to html or text.
        """
        self.outputtype = filetype
        if filetype == 'raw':
            self._hookraw()
        else:
            self._hookhtml()


def main():
    """execute a script"""
    from optparse import OptionParser
    parser = OptionParser(version="pyprof2html %s" % (__version__),
                          usage="Usage: pyprof2html [options] PROFILE_DATA")
    parser.add_option('-r', '--raw', action='store_true',
                      help='raw print mode')
    parser.add_option('-x', '--xhtml', action='store_true',
                      help='html print mode (default)')
    parser.add_option('-t', '--template', dest='template_file',
                      help='jinja2 template file')
    parser.add_option('-n', '--num', type='int', dest='print_functions',
                      default=20, help='print to N funcs.(default 20)')
    parser.add_option('-o', '--output-dir', dest='output_dir', default='html',
                      help='output HTML under the this directory.' \
                           '(default: html)')
    opts, args = parser.parse_args()
    if not len(args):
        parser.parse_args(['-h'])
        return
    p2h = Converter(args[0])
    p2h.functions_number = opts.print_functions
    if opts.template_file:
        p2h.tmpl = ENVIRON.get_template(open(opts.template_file).read())
    if opts.raw:
        outmode = 'raw'
    elif opts.xhtml:
        outmode = 'html'
    else:
        outmode = 'html'
    p2h.output_dir = opts.output_dir
    p2h.printout(outmode)
    if outmode == 'html':
        p2h = Converter(args[0])
        p2h.output_dir = opts.output_dir
        p2h.functions_number = 99999
        p2h.output_htmlfile = 'index-all.html'
        p2h.printout(outmode)


if __name__ == '__main__':
    sys.exit(main())
