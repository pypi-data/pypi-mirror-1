# -*- coding: utf-8 -*-
#
# This file is part of PycWeather
#
# Copyright (c) 2008 Vlad Glagolev <enqlave@gmail.com>. All rights reserved.
#
# Permission to use, copy, modify, and distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

""" pycweather/dmanager.py: weather display manager """

from cStringIO import StringIO
import getopt
import os
import sys
import urllib2

from lxml.etree import parse, tostring, fromstring, XMLSyntaxError

from pycweather import __version__
from pycweather.template import XSL


# correct url to the XOAP service
XOAP_URL = "http://xoap.weather.com/"

# default values stay for Moscow (RU) location, 0 days to display (means only
# current day), metric measurement system and internal XSL stylesheet usage
_CODE = "RSXX0063"
_DAYS = 1
_UNIT = "m"
_XSL = None


def usage():
    print """Usage: %s [options]\n
    -h, --help		show this help
    -v, --version	version information
    -c, --code <code>	location ID code (default is %s)
    -d, --days <days>	number of days to display [1-10] (default is %d)
    -u, --unit <unit>	measurement system [m]etric|[i]mperial (default is %s)
    -s, --search <word>	search for the specified location (city, state, etc.)
    -i, --int		dump internal XSL stylesheet to stdout
    -x, --xsl <file>	custom XSL file\n""" % (sys.argv[0], _CODE, _DAYS, _UNIT)


def version():
    print """PycWeather version:
    %s. (major)
      %s. (minor)
        %s  (revision)""" % tuple(__version__.split("."))
    exit(0)


def search(location):
    data = urllib2.urlopen(XOAP_URL + "search/search?where=%s" % location)

    tree = data.read()

    try:
        xml = fromstring(tree)
    except XMLSyntaxError:
        print "XML syntax error occured while parsing content: ", tree
        exit(2)

    if not xml.getchildren():
        print "No location has been found!"
    elif xml.tag == "error":
        print "Error: %s" % xml.getchildren()[0].text
    else:
        print "Code    | Location\n--------+----------"
        for loc in xml.xpath("loc"):
            print loc.get("id") + ": " + loc.text

        print "--\nTo catch weather information use: %s -c <code>" % sys.argv[0]

    exit(0)


def preview(xml, xsl):
    try:
        xsl_file = parse(xsl) if xsl else fromstring(XSL)
    except XMLSyntaxError:
        print "XML syntax error occured while parsing XSL stylesheet"
        exit(2)

    document = parse(StringIO(tostring(xml)))

    print document.xslt(xsl_file)


def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hvc:d:u:s:ix:", ["help", \
                                   "version", "code=", "days=", "unit=", \
                                   "search=", "int", "xsl="])
    except getopt.error, msg:
        print msg
        usage()
        exit(2)

    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
            exit(0)
        elif o in ("-v", "--version"):
            version()
        elif o in ("-c", "--code"):
            code = a
        elif o in ("-d", "--days"):
            days = int(a) if a != "" else _DAYS
        elif o in ("-u", "--unit"):
            unit = a
        elif o in ("-s", "--search"):
            search(a)
        elif o in ("-i", "--int"):
            print XSL
            exit(0)
        elif o in ("-x", "--xsl"):
            xsl = a

    try:
        code
    except NameError:
        code = _CODE

    try:
        days
    except NameError:
        days = _DAYS

    try:
        unit
    except NameError:
        unit = _UNIT

    try:
        xsl

        if not os.access(xsl, os.R_OK):
            print "Error reading custom XSL file, using internal stylesheet..."
            xsl = _XSL
    except NameError:
        xsl = _XSL

    try:
        data = urllib2.urlopen(XOAP_URL + \
                               "weather/local/%s?cc=*&dayf=%d&unit=%s" % (code,
                               days, unit))
    except:
        print "Unable to connect to %s" % XOAP_URL
        exit(2)

    tree = data.read()

    try:
        xml = fromstring(tree)
    except XMLSyntaxError:
        print "XML syntax error occured while parsing content: ", tree
        exit(2)

    if xml.tag == "error":
        print "Error: %s" % xml.xpath("err")[0].text
    else:
        preview(xml, xsl)
