"""pyprof2html - Profile data convert to HTML.

This script is converted to HTML file from Python's cProfile and
hotshot profiling data.
"""

import os
import sys
import time
from hotshot import log, stats
from pstats import Stats

from jinja2 import Template


__version__ = '0.1.1'
__author__ = 'Hideo Hattori <syobosyobo@gmail.com>'
__licence__ = "New BSD License"

__all__ = ['Converter']

XHTML_HEADER_TEMPLATE = u"""\
<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
<head>

<style type="text/css">
body {
    font-size: 120%;
    line-height: 1.5;
    margin: 0px;
    padding:0px;
}

div.header {
    font-family: Georgia;
    background-color: #eae0d5;
    text-align: right;
    padding: 20px 0px 20px 0px;
    width: 100%;
}
span.header-title {
    font-weight: bold;
    font-size: 250%;
    margin-left: 1em;
    float: left;
}
span.header-time {
    /*font-family: Arial, Verdana;*/
    text-align: right;
    width: 50%;
    margin-right: 1em;
}
div.content {
    clear: both;
    font-family: Arial, Verdana;
}
table.prof {
    border-collapse: collapse;
    border: 1px #cccccc solid;
}
td.prof {
    border-collapse: collapse;
    border: 1px #cccccc solid;
}
span.tdmg {
  margin-left: 5px;
  margin-right: 5px;
}
pre.tdms {
  margin-left: 5px;
  margin-right: 5px;
  margin-top: 0px;
  margin-bottom: 0px;
  font-family: courier new;
  padding: 0px;
}
th.prof {
    border-collapse: collapse;
    border: 1px #cccccc solid;
    background-color: #eae0d5;
}
td.profline {
    border-collapse: collapse;
    border: 1px #cccccc solid;
    font-size: 75%;
    padding:0px;
}
th.procheader {
    align: center;
    background: #a294c8;
}

#sidebar {
    position: fixed;
    padding-top: 30px;
    padding-left:10px;
    padding-right:10px;
    right: 0;
    top  : 0;
    width: 160px;
}

#content {
    margin-left : 1em;
    margin-right: 1em;
    text-align: left;
}

#footer {
    clear     : both;
    text-align: center;
    font-size : small;
    padding   : 10px 0px 10px 0px;
    margin-top:2em;
    margin-bottom: -1em;
    background-color: #eae0d5;
}

div.profilelinetable {
    margin-top: 1em;
}

h1.blog-title {
    margin-top : 0px;
}

</style>
"""

XHTML_BODY_TEMPLATE = u"""\
<title>{{ title }}</title>
</head>

<body>
    <div class="header">
        <span class="header-title">Profile Report</span>
        <span class="header-time">Profile Time on {{ proftime }}</span><br/>
        <span class="header-time">Reported Time on {{ reporttime }}</span>
    </div>

    <div id="sidebar">
    </div>

    <div id="content">
    <p>Total Time     : <span style="font-weight:bold">{{ profdata['totaltime'] }}</span> CPU second<br/>
       Total Func Call: <span style="font-weight:bold">{{ profdata['totalcalls'] }}</span> function calls</p>
    <table class="prof">
        <tr>
        <th class="procheader" align="center" colspan="6">Top {{ profdata['data']|length }} functions data</th>
        </tr>
        <tr align="right">
        <th class="prof"><span class="tdmg">ncalls</span></th>
        <th class="prof"><span class="tdmg">tottime</span></th>
        <th class="prof"><span class="tdmg">percall</span></th>
        <th class="prof"><span class="tdmg">cumtime</span></th>
        <th class="prof"><span class="tdmg">percall</span></th>
        <th class="prof" align="center"><span class="tdmg">filename:lineno(function)</span></th>
        </tr>
        {% for item in profdata['data'] %}
            <tr>
            <td class="prof" align="right"><span class="tdmg">{{ item['ncalls'] }}</span></td>
            <td class="prof" style="background-color:{{ item['tottimelevel'] }}" align="right">
              <span class="tdmg">{{ item['tottime'] }}</span></td>
            <td class="prof" style="background-color:{{ item['totcalllevel'] }}" align="right">
              <span class="tdmg">{{ item['totpercall'] }}</span></td>
            <td class="prof" style="background-color:{{ item['cumtimelevel'] }}" align="right">
              <span class="tdmg">{{ item['cumtime'] }}</span></td>
            <td class="prof" style="background-color:{{ item['cumcalllevel'] }}" align="right">
              <span class="tdmg">{{ item['cumpercall'] }}</span></td>
            {% if item['func'][0] == '~' %}
                <td class="prof"><span class="tdmg">{{ item['func'][2]|escape }}</span></td>
            {% else %}
                <td class="prof"><span class="tdmg">{{ item['func'][0]|escape }} : 
                {{ item['func'][1] }} ({{ item['func'][2]|escape }})</span></td>
            {% endif %}
            </tr>
        {% endfor %}
    </table>
"""

XHTML_LINEBODY_TEMPLATE = u"""\
    <div class="profilelinetable">
    <table class="prof">
    <tr>
    <th class="procheader" align="center" colspan="3">{{ filename }}</th>
    </tr>
    <tr align="right">
    <th class="prof" align="center"><span class="tdmg">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;time&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</span></th>
    <th class="prof" align="center"><span class="tdmg">num</span></th>
    <th class="prof" align="center"><span class="tdmg">code</span></th>
    </tr>
    {% for item in profdata %}
        <tr>
        {% if item['sec'] == 'None' %}
            <td class="profline" align="right"><span class="tdms"></span></td>
        {% else %}
            <td class="profline" align="right" style="background-color:#ffffff;"><span class="tdms">{{ item['sec'] }} sec</span></td>
        {% endif %}
        <td class="profline" align="right"><span class="tdms" style="color:#999999;">{{ loop.index }}</span></td>
        {% if item['sec'] == 'None' %}
            <td class="profline" align="left"><pre class="tdms">{{ item['line']|escape }}</pre></td>
        {% else %}
            <td class="profline" align="left"><pre class="tdms" style="font-weight:bold;">{{ item['line']|escape }}</pre></td>
        {% endif %}
        </tr>
    {% endfor %}
    </table>
    </div>
"""

XHTML_FOOTER_TEMPLATE = """\
    </div>
    <div id="footer">
    <p>
    Powered by <a href="http://www.python.org/">Python</a> and 
    <a href="http://jinja.pocoo.org/2/">Jinja2</a>&nbsp;&nbsp;&nbsp;
    <a href="http://pypi.python.org/pypi/pyprof2html/">pyprof2html</a>: %s
    </p>
    </div>
</body></html>
""" % __version__


def check_hotlinetimings(dump):
    """check to linetimings hotshot-profile datafile."""
    signature = "yes"
    return signature in dump

def check_hotshot(dump):
    """check to hotshot-profile datafile."""
    signature = "hotshot-version"
    return signature in dump


class Converter:
    """output to HTML from profile data"""

    def __init__(self, filename):
        self.proftype = None
        dump = open(filename).read()
        if check_hotshot(dump[:20]):
            self.prof = stats.load(filename)
            self.tmpl = Template(XHTML_BODY_TEMPLATE)
            if check_hotlinetimings(dump[102:108]):
                self.profline = log.LogReader(filename)
                self.proftype = 'line'
                self.tmplline = Template(XHTML_LINEBODY_TEMPLATE)
        else:
            self.prof = Stats(filename)
            self.tmpl = Template(XHTML_BODY_TEMPLATE)
        self.filename = filename
        self.proftime = time.ctime(os.stat(filename).st_mtime)
        self.outputtype = 'html'
        self.functions_number = 20
        self.levelmap = {
            0: '',
            1: '#fa9cb8',
            2: '#e95464',
            3: '#e2041b',
        }

    def _printhtml_onesource(self, filename, profinfo):
        num = 0
        result = []
        try:
            lines = open(filename).readlines()
        except IOError:
            return ""
        codec = None
        for line in lines:
            ## TODO: Oops... I don't absolute to this 'UnicodeDecodeError'.
            ## darty hack
            try:
                line.decode(sys.getdefaultencoding())
            except UnicodeDecodeError:
                line = "Unicode Decoding Error!!!"
            num += 1
            if profinfo.has_key(num):
                result.append({'sec':profinfo[num], 'line':line})
            else:
                result.append({'sec':'None', 'line':line})
        return self.tmplline.render(filename=filename,
                                    profdata=result,
                                    codec=codec)

    def _print_onesource(self, filename, profinfo):
        num = 0
        result = []
        try:
            lines = open(filename).readlines()
        except IOError:
            return ""
        result.append("="*60 + "\n")
        result.append(filename + "\n")
        result.append("="*60 + "\n")
        for line in lines:
            num += 1
            if profinfo.has_key(num):
                result.append(" %3.4lfsec | %s" % (profinfo[num], line))
            else:
                result.append("           | %s" % (line))
        return ''.join(result)

    def _print_source(self, profinfo):
        source_list = []
        info = {}
        filename = None
        filecnt  = 0
        for prof in profinfo:
            filename = prof[0]
            if not source_list.count(filename):
                if info != {}:
                    filecnt += 1
                    if self.outputtype == 'html':
                        print self._printhtml_onesource(source_list[filecnt-1],
                                                        info)
                    else:
                        print self._print_onesource(source_list[filecnt-1], info)
                info = {}
                source_list.append(filename)
            info[prof[1]] = prof[2]
        if self.outputtype == 'html':
            print self._printhtml_onesource(filename, info)
        else:
            print self._print_onesource(filename, info)

    def _analyze_profline(self):
        profset = dict()
        for i in self.profline:
            if not profset.has_key(i[1]):
                profset[i[1]] = float(int(i[2])/1000000.)
            else:
                profset[i[1]] += float(int(i[2])/1000000.)
        proflist = [(prof[0], prof[1], profset[prof]) for prof in profset]
        proflist.sort()
        return proflist

    def _hookraw(self):
        if self.proftype == 'line':
            proflist = self._analyze_profline()
            self._print_source(proflist)
        else:
            self.prof.sort_stats('time', 'calls')
            self.prof.print_stats()

    def _analyzed_prof(self):
        self.prof.sort_stats('time', 'calls')
        null = open('/dev/null', 'w')   # darty hack (order output block)
        self.prof.stream = null
        backstream = self.prof.stream
        tmp, funclist = self.prof.get_print_list(())
        self.prof.stream = backstream
        null.close()
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
            tottime = "%8.4lf" % stat[2]
            try:
                totpercall = "%8.4lf" % float(stat[2]/stat[0])
            except ZeroDivisionError:
                totpercall = "0.0000"
            cumtime = "%8.4lf" % stat[3]
            try:
                cumpercall = "%8.4lf" % float(stat[3]/stat[0])
            except ZeroDivisionError:
                cumpercall = "0.0000"
            tottlevel = self.levelmap[int((stat[2]/self.prof.total_tt)*3.33)]
            tmp = int((float(totpercall)/self.prof.total_tt)*3.33)
            totclevel = self.levelmap[tmp]
            cumtlevel = self.levelmap[int((stat[3]/self.prof.total_tt)*3.33)]
            tmp = int((float(cumpercall)/self.prof.total_tt)*3.33)
            cumclevel = self.levelmap[tmp]
            data = {
                'ncalls'        : ncalls,
                'tottime'       : tottime,
                'cumtime'       : cumtime,
                'totpercall'    : totpercall,
                'cumpercall'    : cumpercall,
                'cumtimelevel'  : cumtlevel,
                'tottimelevel'  : tottlevel,
                'totcalllevel'  : totclevel,
                'cumcalllevel'  : cumclevel,
                'func'          : func,
            }
            datalist.append(data)
        profdata = {
            'totaltime': "%8.4lf" % self.prof.total_tt,
            'totalcalls': self.prof.total_calls,
            'data': datalist
        }
        return profdata

    def _hookhtml(self):
        profdata = self._analyzed_prof()
        print XHTML_HEADER_TEMPLATE
        print self.tmpl.render(title="pyprof2html - %s" % self.filename,
                               proftime=self.proftime,
                               reporttime=time.ctime(),
                               profdata=profdata)
        if self.proftype:
            profinfo = self._analyze_profline()
            self._print_source(profinfo)
        print XHTML_FOOTER_TEMPLATE

    def printout(self, filetype='html'):
        """print to html or text."""
        self.outputtype = filetype
        hookpoint = None
        if filetype == 'raw':
            hookpoint = self._hookraw
        else:
            hookpoint = self._hookhtml
        hookpoint()


def main():
    """execute a script"""
    from optparse import OptionParser
    parser = OptionParser(version="%s version:%s" % (__file__, __version__),
                          usage="Usage: pyprof2html [options] arg1")
    parser.add_option('-r', '--raw', action='store_true',
                      help='raw print mode')
    parser.add_option('-x', '--xhtml', action='store_true',
                      help='html print mode (default)')
    parser.add_option('-t', '--template', dest='template_file',
                      help='jinja2 template file')
    parser.add_option('-n', '--num', type='int', dest='print_functions',
                      default=20, help='print to N funcs.(default 20)')
    opts, args = parser.parse_args()
    if not len(args):
        parser.parse_args(['-h'])
        return
    p2h = Converter(args[0])
    p2h.functions_number = opts.print_functions
    if opts.template_file:
        p2h.tmpl = Template(open(opts.template_file).read())
    if opts.raw:
        outmode = 'raw'
    elif opts.xhtml:
        outmode = 'html'
    else:
        outmode = 'html'
    p2h.printout(outmode)


if __name__ == '__main__':
    sys.exit(main())

