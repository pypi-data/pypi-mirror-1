#!/usr/bin/python
"""generate coverage report for xix-utils
(or any other python package)
"""

from xix.utils.cover import AnnotationParser, annotationToXML, annotationToHTML
from xix.utils.cover import CoverageReportParser, reportToXML, _XSLT
from optparse import OptionParser

import lxml.etree as ET

import os, sys, time
from datetime import datetime
from shutil import copy2, copytree, rmtree
from glob import glob
from xix import getoutput, resource_filename
from StringIO import StringIO

__author__ = 'Drew Smathers'

pj = os.path.join

def _path(unixpath):
    return unixpath.replace('/', os.path.sep)

def _mkdir(path):
    base, _base = os.path.split(path)
    if base and not os.path.exists(base):
        _mkdir(base)
    if not os.path.exists(path):
        os.mkdir(path)

def utcasctime():
    dt = datetime.utcnow()
    asctime = time.asctime(dt.utctimetuple())
    return asctime

def prepare_fs(source, copy_compiled=True, exclude=[], depends=[]):
    target = '.xcoverage'
    if os.path.exists(target):
        rmtree(target)
    for root, dirs, files in os.walk(source):
        target_dir = pj(target, root)
        _mkdir(target_dir)
        cfiles = [ f for f in files if f[-6:] != ',cover' ]
        if not copy_compiled:
            cfiles = [ f for f in cfiles if f[-4:] not in ('.pyo', '.pyc') ]
        for file in cfiles:
            copy2(pj(root, file), pj(target_dir, file))
        [ dirs.remove(ex) for ex in exclude if ex in dirs ]
    for patt in depends:
        srcs = glob(patt)
        for src in srcs:
            if os.path.isdir(src):
                dst = pj(target, src)
                copytree(src, dst)
            else:
                copy2(src, target)
    cvg = pj(target, 'coverage.py')
    if not os.path.exists(cvg):
        copy2('.coverage.py', cvg)

def annotate(source):
    args = []
    for root, dirs, files in os.walk(source):
        args.extend(glob(pj(root, '*.py')))
    fd =  open('.report', 'w')
    cmd = 'python coverage.py -a -r -m %s' % ' '.join(args)
    output = getoutput(cmd)
    fd.write(output)
    fd.close()

def generateXML(reportdir, source, annotationXSLT=None):
    print 'Generated coverage annotations'
    parser = AnnotationParser()
    for root, dirs, files in os.walk(pj(source)):
        covers = [ f for f in files if f[-6:] == ',cover' ]
        for cover in covers:
            srcname = pj(root, cover.split(',cover')[0])
            srcname = srcname.replace(os.path.sep, '.')[:-3]
            print 'generating XML/HTML for : ', srcname
            xml_fname = 'coverage_' + srcname.replace('.', '-') + '.xml'
            html_fname = 'coverage_' + srcname.replace('.', '-') + '.html'
            annt = parser.parse(open(pj(root, cover)))
            xml = annotationToXML(annt, tree=True)
            fd = open(pj(reportdir, xml_fname), 'w')
            xml.write(fd)
            if not annotationXSLT:
                xslt = ET.parse(StringIO(_XSLT))
            else:
                xslt = ET.parse(open(annotationXSLT))
            transform = ET.XSLT(xslt)
            html = transform(xml, modname="'%s'" % srcname)
            fd.close()
            fd = open(pj(reportdir, html_fname), 'w')
            html.write(fd)
            fd.close()

_REPORT_XSLT = '''<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
<xsl:output method="html"/>
<xsl:param name="packagename"/>
<xsl:param name="utctime"/>
<xsl:template match="/">
    <html><head><title>Coverage Report for <xsl:value-of select="$packagename"/></title>
    <link rel="stylesheet" type="text/css" href="coverage.css"/></head>
    <body>
    <h2>Coverage Report for <xsl:value-of select="$packagename"/></h2>
    <table><tr><th>Module Name</th><th>Statements</th><th>Executed</th><th>Coverage</th></tr>
    <xsl:for-each select="//module">
        <tr>
            <td class="report-column">
                <a>
                <xsl:attribute name="href">
                   <xsl:text>coverage_</xsl:text><xsl:value-of select="translate(@name, '.', '-')"/><xsl:text>.html</xsl:text>
                </xsl:attribute>
                <xsl:value-of select="@name"/>
                </a>
            </td>
            <td class="report-column"><xsl:value-of select="@statements"/></td>
            <td class="report-column"><xsl:value-of select="@executed"/></td>
            <td class="report-column"><xsl:value-of select="@coverage"/></td>
        </tr>
    </xsl:for-each>
    <xsl:for-each select="//summary">
        <tr class="summary">
            <td class="report-column">TOTAL
            </td>
            <td class="report-column"><xsl:value-of select="@statements"/></td>
            <td class="report-column"><xsl:value-of select="@executed"/></td>
            <td class="report-column"><xsl:value-of select="@coverage"/></td>
        </tr>
    </xsl:for-each>
    </table>
    <div id="colophon">Report generated on <xsl:value-of select="$utctime"/> GMT<br/>
    xix-coverage.py (<a href="http://xix.python-hosting.com">http://xix.python-hosting.com</a>)<br/>
    coverage.py (<a href="http://www.nedbatchelder.com/code/modules/coverage.html">
    http://www.nedbatchelder.com/code/modules/coverage.html</a>)<br/>
    (C) 2006 Drew Smathers &lt;drew smathers at gmail com&gt;<br/>
    </div>
    </body></html>
</xsl:template>
</xsl:stylesheet>'''

def generateIndex(reportdir, source, reportXSLT=None):
    report = CoverageReportParser().parse(open('.report'))
    xml = reportToXML(report, tree=True)
    if not reportXSLT:
        xslt = ET.parse(StringIO(_REPORT_XSLT))
    else:
        xslt = ET.parse(open(reportXSLT))
    transform = ET.XSLT(xslt)
    html = transform(xml, packagename="'%s'" % source, utctime="'%s'" % utcasctime())
    fd = open(pj(reportdir, 'index.html'), 'w')
    html.write(fd)
    fd.close()

def main(opts):
    if not os.path.exists('.coverage.py'):
        path = resource_filename('xix', pj('data', 'coverage.py'))
        copy2(path, '.coverage.py')
    prepare_fs(opts.source, opts.copy_compiled, opts.exclude_dirs, opts.depends)
    _mkdir(opts.report_dir)
    reportdir = os.path.abspath(opts.report_dir)
    os.chdir('.xcoverage')
    print getoutput('python coverage.py -x %s' % opts.command)
    annotate(opts.source)
    generateXML(reportdir, opts.source, opts.annotation_xslt)
    generateIndex(reportdir, opts.source, opts.report_xslt)
    # Copy over html assets (.png, .css files etc.)
    for asset in options.html_assets:
        copy2(asset, reportdir)
    if not options.html_assets: # make it perty by default
        fn = resource_filename('xix', pj('data', 'coverage.css'))
        copy2(fn, reportdir)
    print 'Report complete. See ' + pj(reportdir, 'index.html')
    

def getrunner(opts, args):
    if os.path.exists(opts.command):
        return opts.command + ' '.join(args)
    else:
        return ' '.join(args)

if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option('-s', '--source', default='xix', dest='source',
            help='source directory to generate coverage report for')
    parser.add_option('-d', '--depends', dest='depends', default='*.py,*cfg,tests',
            help='dependencies (pipe-seperated list of files/directories) ' \
                'in current working directory')
    parser.add_option('-c', action='store_true', dest='copy_compiled',
            help='copy over *.pyc and *.pyo files from source.')
    parser.add_option('-r','--report-directory', dest='report_dir', default='build/reports/coverage',
            help='target directory for coverage reports.')
    parser.add_option('-x', '--exclude-dirs', dest='exclude_dirs', default='.svn',
            help='comma-separated list of directories to exclude in source tree copy.')
    parser.add_option('-t', '--test-runner', dest='command', default='runtests.py',
            help='test runner module')
    parser.add_option('-a', '--annotation-xslt', dest='annotation_xslt',
            help='xslt source file for generating module coverage annotation html')
    parser.add_option('-m', '--report-xslt', dest='report_xslt',
            help='xslt source file for generating index.html')
    parser.add_option('-z', '--html-assets', dest='html_assets',
            help='comma-separated list of css, image files etc. to copy to report directory')
    options, args = parser.parse_args()
    options.command = getrunner(options, args)
    options.depends = [ _path(p) for p in options.depends.split(',') ]
    options.exclude_dirs = options.exclude_dirs.split(',')
    if options.report_xslt:
        options.report_xslt = os.path.abspath(_path(options.report_xslt))
    if options.annotation_xslt:
        options.annotation_xslt = os.path.abspath(_path(options.annotation_xslt))
    if options.html_assets:
        options.html_assets = [ os.path.abspath(_path(a)) for a in options.html_assets.split(',') ]
    else:
        options.html_assets = []
    main(options)

