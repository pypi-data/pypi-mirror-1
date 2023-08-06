# -*- coding: utf-8 -*-
#
# This file is part of PycWeather
#
# Copyright (c) 2009 Vlad Glagolev <enqlave@gmail.com>
# All rights reserved.
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

""" pycweather/weather.py: Weather class """

from cStringIO import StringIO
from urllib2 import urlopen

from lxml.etree import parse, tostring, fromstring, XMLSyntaxError

from pycweather import __version__


# correct url to the XOAP service
XOAP_URL = "http://xoap.weather.com/"


class Weather:

    def __init__(self):
        self.xsl = None
        self.id = None
        self.key = None

    def auth(self, credentials):
        try:
            self.id, self.key = credentials.split(":")
        except:
            print "Invalid credentials"

    def search(self, location):
        data = urlopen(XOAP_URL + "search/search?where=%s" % location)

        tree = data.read()

        try:
            xml = fromstring(tree)
        except XMLSyntaxError:
            print "XML syntax error occured while parsing content: ", tree

            return -1

        if not xml.getchildren():
            print "No location has been found!"
        elif xml.tag == "error":
            print "Error: %s" % xml.getchildren()[0].text
        else:
            print "Code    | Location\n--------+----------"
            for loc in xml.xpath("loc"):
                print loc.get("id") + ": " + loc.text

            print "--\nTo catch weather information use: pycweather -c <code>"

    def load(self, xsl_file):
        try:
            self.xsl = parse(xsl_file)
        except XMLSyntaxError:
            print "XML syntax error occured while parsing XSL stylesheet"
        except:
            print "Unable to read XSL file"

    def preview(self, code, days, unit):
        try:
            data = urlopen(XOAP_URL + \
                   "weather/local/%s?cc=*&dayf=%d&unit=%s&par=%s&key=%s" % \
                   (code, days, unit, self.id, self.key))
        except:
            print "Unable to connect to %s" % XOAP_URL

            return -1

        tree = data.read()

        try:
            xml = fromstring(tree)
        except XMLSyntaxError:
            print "XML syntax error occured while parsing content: ", tree

            return -1

        if xml.tag == "error":
            print "Error: %s" % xml.xpath("err")[0].text

            return -1
        else:
            document = parse(StringIO(tostring(xml)))

        print document.xslt(self.xsl)
