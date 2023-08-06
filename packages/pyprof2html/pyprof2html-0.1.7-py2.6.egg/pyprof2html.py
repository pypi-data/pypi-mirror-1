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

from jinja2 import Template


__version__ = '0.1.7'
__licence__ = 'New BSD License'
__author__ = 'Hideo Hattori <syobosyobo@gmail.com>'

__all__ = ['Converter']

XHTML_HEADER_TEMPLATE = u"""\
<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
 "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
<head>

<style type="text/css">
body { font-size: 120%; line-height: 1.5; margin: 0px; padding:0px; }
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
span.header-time { text-align: right; width: 50%; margin-right: 1em; }
div.content { clear: both; font-family: Arial, Verdana; }
table.prof { border-collapse: collapse; border: 1px #cccccc solid; }
td.prof { border-collapse: collapse; border: 1px #cccccc solid; }
span.tdmg { margin-left: 5px; margin-right: 5px; }
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
td.profline_r {
    border-collapse: collapse;
    border: 1px #cccccc solid;
    font-size: 75%;
    padding:0px 1px 0px 0px;
    text-align: right;
}
td.profline_l {
    border-collapse: collapse;
    border: 1px #cccccc solid;
    font-size: 75%;
    padding:0px 1px 0px 0px;
    text-align: left;
}
th.procheader { align: center; background: #a294c8; }
#sidebar {
    position: fixed;
    padding-top: 30px;
    padding-left:10px;
    padding-right:10px;
    right: 0;
    top: 0;
    width: 160px;
}
#content { margin-left: 1em; margin-right: 1em; text-align: left; }
#footer {
    clear     : both;
    text-align: center;
    font-size : small;
    padding   : 10px 0px 10px 0px;
    margin-top:2em;
    margin-bottom: -1em;
    background-color: #eae0d5;
}
div.profilelinetable { margin-top: 1em; }
div.header a { color: #000000; }
div.header a:visited { color: #000000; }
div.header a:hover { color: #000000; }

</style>
"""

XHTML_BODY_TEMPLATE = u"""\
<title>{{ title }}</title>
</head>

<body>
    <div class="header">
        <span class="header-title"><a href="./index.html"
        >Profile Report</a></span>
        <span class="header-time">Profile Time on {{ proftime }}</span><br/>
        <span class="header-time">Reported Time on {{ reporttime }}</span>
    </div>

    <div id="sidebar">
    </div>

    <div id="content">
    <p>Total Time     : <span style="font-weight:bold"
                        >{{ profdata['totaltime'] }}</span> CPU second<br/>
       Total Func Call: <span style="font-weight:bold"
                        >{{ profdata['totalcalls'] }}</span
                        > function calls</p>
    <table class="prof">
        <tr>
            <th class="procheader" align="center" colspan="6"
            >Top {{ profdata['data']|length }} functions data &#40;<a href="
            {% if thisname == 'index.html' %}
                index-all.html">all function</a>&#41;</th>
            {% else %}
                index.html">top 20 function</a>&#41;</th>
            {% endif %}
        </tr>
        <tr align="right">
        <th class="prof"><span class="tdmg"
                               title="for the number of calls"
                               >ncalls</span></th>
        <th class="prof"
        ><span class="tdmg" title="for the total time spent in the given
 function (and excluding time made in calls to sub-functions)"
        >tottime</span></th>
        <th class="prof"
        ><span class="tdmg" title="the quotient of tottime divided by ncalls"
        >percall</span></th>
        <th class="prof"
        ><span class="tdmg" title="total time spent in this and all
 subfunctions (from invocation till exit).
 This figure is accurate even for recursive functions.">cumtime</span></th>
        <th class="prof"
        ><span class="tdmg"
        title="the quotient of cumtime divided by primitive calls"
        >percall</span></th>
        <th class="prof" align="center"
        ><span class="tdmg"
               title="provides the respective data of each function"
        >filename:lineno(function)</span></th>
        </tr>
        {% for item in profdata['data'] %}
            <tr>
            <td class="prof"
                style="background-color:{{ item['ncallslevel'] }}"
                align="right">
              <span class="tdmg">{{ item['ncalls'] }}</span></td>
            <td class="prof"
                style="background-color:{{ item['tottimelevel'] }}"
                align="right">
              <span class="tdmg">{{ item['tottime'] }}</span></td>
            <td class="prof"
                style="background-color:{{ item['totcalllevel'] }}"
                align="right">
              <span class="tdmg">{{ item['totpercall'] }}</span></td>
            <td class="prof"
                style="background-color:{{ item['cumtimelevel'] }}"
                align="right">
              <span class="tdmg">{{ item['cumtime'] }}</span></td>
            <td class="prof"
                style="background-color:{{ item['cumcalllevel'] }}"
                align="right">
              <span class="tdmg">{{ item['cumpercall'] }}</span></td>
            {% if item['func'][0] == '~' %}
                <td class="prof"
                 ><span class="tdmg">{{ item['func'][2]|escape }}</span></td>
            {% else %}
                <td class="prof"><span class="tdmg"
                {% if proftype == 'line' %}
                    {% if item['linelink'][0] != "<" %}
                        ><a href="{{ item['linelink']|escape }}"
                        >{{ item['func'][0]|escape }}</a
                        > : <a href="{{ item['linelink']|escape }}#line{{ \
                                item['func'][1] }}"
                        >{{ item['func'][1] }}</a> &#40;
                         {{ item['func'][2]|escape }}&nbsp;&#41;</span></td>
                    {% else %}
                        >{{ item['func'][0]|escape }} :
                         {{ item['func'][1] }} &#40;
                         {{ item['func'][2]|escape }}&nbsp;&#41;</span></td>
                    {% endif %}
                {% else %}
                    >{{ item['func'][0]|escape }} :
                     {{ item['func'][1] }} &#40;
                     {{ item['func'][2]|escape }}&nbsp;&#41;</span></td>
                {% endif %}
            {% endif %}
            </tr>
        {% endfor %}
    </table>
"""

XHTML_LINEBODY_TEMPLATE = u"""\
<title>{{ title }}</title>
</head>

<body>
    <div class="header">
        <span class="header-title"><a href="./index.html"
        >Profile Report</a></span>
        <span class="header-time">Profile Time on {{ proftime }}</span><br/>
        <span class="header-time">Reported Time on {{ reporttime }}</span>
    </div>

    <div id="sidebar">
    </div>

    <div id="content">
    <p>Total Time     : <span style="font-weight:bold"
                        >{{ profdata['totaltime'] }}</span> CPU second<br/>
       Total Func Call: <span style="font-weight:bold"
                        >{{ profdata['totalcalls'] }}</span
                        > function calls</p>
    <div class="profilelinetable">
    <table class="prof">
    <tr>
    <th class="procheader" align="center" colspan="4">{{ filename }}</th>
    </tr>
    <tr align="right">
    <th class="prof" align="center"><span class="tdmg">num</span></th>
    <th class="prof" align="center"><span class="tdmg"
     >&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;time&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</span
     ></th>
    <th class="prof" align="center"><span class="tdmg">calls</span></th>
    <th class="prof" align="center"><span class="tdmg">code</span></th>
    </tr>
    {% for item in profdata['data'] %}
        <tr>
        <td id="line{{ loop.index }}" class="profline_r"
        ><span class="tdms" style="color:#999999;">{{ loop.index }}</span></td>
        {% if item['sec'] == 'None' %}
            <td class="profline_r"><span class="tdms"></span></td>
            <td class="profline_r"><span class="tdms"></span></td>
        {% else %}
            <td class="profline_r" style="background-color:#ffffff;"
            ><span class="tdms">{{ item['sec'] }} sec</span></td>
            <td class="profline_r" style="background-color:#ffffff;"
            ><span class="tdms">{{ item['cnt'] }} call</span></td>
        {% endif %}
        {% if item['sec'] == 'None' %}
            <td class="profline_l"
             ><pre class="tdms">{{ item['line']|escape }}</pre></td>
        {% else %}
            <td class="profline_l"><pre class="tdms" style="font-weight:bold;"
             >{{ item['line']|escape }}</pre></td>
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
    Powered by <a href="http://www.python.org/">Python</a
    > and <a href="http://jinja.pocoo.org/2/">Jinja2</a>&nbsp;&nbsp;&nbsp;
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


def mapping_table(target, nall):
    levelmap = {0: '#ccffcc',   ## yellow green (light)
                1: '#66ff99',   ## yellow green
                2: '#ffcc33',   ## orange
                3: '#ff6666',   ## pink
                4: '#ff3333',   ## red
                }
    levels = [nall*0.01, nall*0.03, nall*0.08, nall*0.12, nall*0.20]
    for level in range(len(levels)):
        if target < levels[level]:
            return levelmap[level]
    return levelmap[len(levelmap)-1]


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


class Converter(object):
    """output to HTML from profile data
    """

    def __init__(self, filename):
        self.outfile = None
        self.output_dir = 'html'
        self.output_htmlfile = 'index.html'
        self.proftype = None
        dump = open(filename).read()
        if check_hotshot(dump[:20]):
            self.prof = stats.load(filename)
            self.tmpl = Template(XHTML_BODY_TEMPLATE)
            if check_hotlinetimings(dump[102:108]):
                self.profline = log.LogReader(filename)
                self.proftype = 'line'
                self.tmplline = Template(XHTML_HEADER_TEMPLATE + \
                                         XHTML_LINEBODY_TEMPLATE + \
                                         XHTML_FOOTER_TEMPLATE)
        else:
            self.prof = Stats(filename)
            self.tmpl = Template(XHTML_BODY_TEMPLATE)
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
        for num, line in enumerate(fileobj):
            if num+1 in profs:
                result.append({'sec': profs[num+1]['sec'],
                               'cnt': profs[num+1]['cnt'],
                               'line': line})
            else:
                result.append({'sec': 'None', 'line': line})
        titletext = "pyprof2html - %s" % filename
        renderdict = {'title': titletext,
                      'proftime': self.proftime,
                      'reporttime': self.reporttime,
                      'filename': filename,
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
        num = 0
        result = []
        if not os.path.exists(filename):
            return ""
        result.append("="*60 + "\n")
        result.append(filename + "\n")
        result.append("="*60 + "\n")
        for line in open(filename):
            num += 1
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
        sources = []
        info = {}
        filecnt = 0
        for i, prof in enumerate(profs):
            filename = prof[0]
            if (not sources.count(filename)) or (len(profs) == (i+1)):
                if info != {}:
                    if self.outputtype == 'html':
                        out_filename = "%s/%s.html" % (self.output_dir,
                                       sources[filecnt].replace('/', '_'))
                        outputfile = open(out_filename, 'w')
                        self._printhtml_source(sources[filecnt],
                                               info, outputfile)
                        outputfile.close()
                    else:
                        print self._print_source(sources[filecnt], info)
                    filecnt += 1
                info = {}
                sources.append(filename)
            info[prof[1]] = {'sec': prof[2], 'cnt': prof[3]}

    def _analyze_profline(self):
        """analyzed to hotshot linetimings data.
        """
        profset = dict()
        for i in self.profline:
            if i[0] == 0 or i[0] == 1:  # WHAT_ENTER or WHAT_EXIT
                continue
            if i[1] not in profset:
                profset[i[1]] = [float(int(i[2])/1000000.), i[2]]
            else:
                profset[i[1]][0] += float(int(i[2])/1000000.)
                profset[i[1]][1] += i[2]
        profs = [(p[0], p[1], profset[p][0], profset[p][1]) for p in profset]
        profs.sort()
        return profs

    def _analyzed_prof(self):
        """analyzed to not linetimings profile data.
        """
        self.prof.sort_stats('time', 'calls')
        self.prof.stream = open(os.devnull, 'w')    ## darty hack
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
        if self.proftype == 'line':
            profs = self._analyze_profline()
            self._print_sources(profs)
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
        print >> self.outfile, XHTML_HEADER_TEMPLATE
        print >> self.outfile, self.tmpl.render(title=titletext,
                                                proftime=self.proftime,
                                                reporttime=self.reporttime,
                                                profdata=profdata,
                                                thisname=self.output_htmlfile,
                                                proftype=self.proftype)
        if self.proftype:
            profs = self._analyze_profline()
            self._print_sources(profs)
        print >> self.outfile, XHTML_FOOTER_TEMPLATE
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
        p2h.tmpl = Template(open(opts.template_file).read())
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
