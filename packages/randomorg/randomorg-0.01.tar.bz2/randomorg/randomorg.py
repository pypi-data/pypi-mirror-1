#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set sw=4 ts=4 sts=4 et tw=79 :
# Copyright 2008 Ali Polatel <polatel@itu.edu.tr>
# Distributed under the terms of the GNU General Public License v3

"""Module to access random.org for random numbers

Examples
========

Dice
----

>>> import randomorg
>>> ro = randomorg.RandomOrg()
>>> if ro.checkQuota():
...:    # Roll a dice
...:    print ro.getInteger(2, 1, 6)

Feed /dev/random
----------------

>>> import os
>>> import randomorg
>>> rfp = "/dev/random"
>>> ro = randomorg.RandomOrg()
>>>
>>> if os.access(rfp, os.W_OK):
...:    fp = open(rfp, "a")
...:    # Old API uses checkBuffer instead of checkQuota
...:    if ro.checkBuffer():
...:        for bytes in ro.getRandomByte():
...:            fp.write(bytes)
...:    close(fp)
"""

__name__ = "randomorg"
__version__ = "0.01"
__author__ = "Ali Polatel <polatel@itu.edu.tr>"
__license__ = "GPL-3"
__url__ = "http://hawking.nonlogic.org/projects/randomorg/"

__all__ = [ "RandomOrgHTTPError", "RandomOrg", "getPage" ]

import os
import sys
import socket
import urllib2
import warnings

LF = '\n'
TAB = '\t'

class RandomOrgHTTPError(urllib2.HTTPError):
    """HTTPError that also prints out random.org error messages."""
    
    def __str__(self):
        return 'HTTP Error %s(%s): %s' % (self.code, self.msg,
                self.read().strip('Error: ').rstrip(LF))

def getPage(uri, headers):
    """Get an url, raise RandomOrgHTTPError on failure.

    @param uri: The requested url address.
    @type uri: str

    @param headers: HTTP Headers passed to urllib2.Request()
    @type headers: dict
    """

    req = urllib2.Request(uri, None, headers)
    
    try:
        handle = urllib2.urlopen(req)
    except urllib2.HTTPError, err:
        raise RandomOrgHTTPError(err.url, err.code, err.msg, err.hdrs, err.fp)
    
    return handle.read()

class RandomOrg:
    """Main class to interact with random.org"""
    
    def __init__(self, uri="http://www.random.org"):
        """Initialize class.

        @param uri: random.org url.
        @type uri: str
        """

        self.uri = uri

        self.name = 'randomorg.py ' + __version__
        self.mail = __author__[__author__.find('<') + 1:__author__.rfind('>')]
        
        self.headers = dict()
        self.headers['User-Agent'] = "%s (%s)" % (self.name, self.mail)

        self.limits = { "columnMin" : 1,
                "columnMax" : 10e8,
                "maxNum" : 10e4,
                "intMin" : -10e8,
                "intMax" : 10e8,
                "strMin" : 1,
                "strMax" : 20,
                "maxBytes" : 16384,
                "seqRange" : 10e4,
                "seqMin" : -10e8,
                "seqMax" : 10e8 }

    def getInteger(self, num, minimum=-10e8, maximum=10e8,
            columns=1, base=2, format="plain", rnd="new",
            headers=None, link="integers/"):
        """Interact with random.org integer generator.

        @param num: The number of integers requested.
        @type num: int

        @param minimum: The smallest value allowed for each integer.
        @type minimum: int

        @param maximum: The largest value allowed for each integer.
        @type maximum: int

        @param columns: The number of columns in which the integers will be arranged.
        @type columns: int

        @param base: The base that will be used to print the numbers, i.e.,
            binary, octal, decimal or hexadecimal.
        @type base: int

        @param format: Determines the return type of the document that the
            server produces as its response. If html is specified, the server
            produces a nicely formatted XHTML document (MIME type text/html),
            which will display well in a browser but which is somewhat
            cumbersome to parse. If plain is specified, the server produces as
            minimalistic document of type plain text (MIME type text/plain)
            document, which is easy to parse. If you are writing an automated
            client, you probably want to specify plain here.
        @type format: str

        @param rnd: Determines the randomization to use to generate the
            numbers. If new is specified, then a new randomization will created
            from the truly random bitstream at RANDOM.ORG. This is probably what
            you want in most cases. If id.identifier is specified, the identifier
            is used to determine the randomization in a deterministic fashion from
            a large pool of pregenerated random bits. Because the numbers are
            produced in a deterministic fashion, specifying an id basically uses
            RANDOM.ORG as a pseudo-random number generator. The third
            (date.iso-date) form is similar to the second; it allows the
            randomization to be based on one of the daily pregenerated files. This
            form must refer to one of the dates for which files exist, so it must
            be a day in the past. The date must be in ISO 8601  format (i.e.,
            YYYY-MM-DD).
        @type rnd: str

        @param headers: The HTTP headers to send. Passed to urllib2.Request()
        @type headers: dict

        @param link: The relative link to the integers script.
        @type link: str
        
        @return: If format is "plain", a tuple of integers will be returned,
            else the html page is returned as a string.
        """

        if num > self.limits["maxNum"]:
            msg = "The number of integers is limited to %d"
            raise OverflowError, msg % self.limits["maxNum"]
        if minimum < self.limits["intMin"]:
            msg = "The lower bound of the interval is limited to %d"
            raise OverflowError, msg % self.limits["intMin"]
        if maximum > self.limits["intMax"]:
            msg = "The upper bound of the interval is limited to %d"
            raise OverflowError, msg % self.limits["intMax"]
        if columns < self.limits["columnMin"] or columns > self.limits["columnMax"]:
            msg = "columns must be between %d and %d"
            raise OverflowError, msg % (self.limits["columnMin"],
                    self.limits["columnMax"])
        if base not in (2, 8, 10, 16):
            raise TypeError, "Bad base"
        if format not in ("html", "plain"):
            raise TypeError, "Bad format"
    
        if headers is None:
            headers = self.headers

        uri = "/".join((self.uri, link)) +\
            "?num=%d&min=%d&max=%d&col=%d&base=%d&format=%s&rnd=%s" % \
            (num, minimum, maximum, columns, base, format, rnd)
        data = getPage(uri, headers)

        if format == "plain":
            datalist = data.split(LF)
            datalist.remove('')

            t = []
            for element in datalist:
                if TAB in element:
                    y = []
                    for elem in element.split(TAB):
                        y.append(int(elem, base=base))
                    t.append(tuple(y))
                else:
                    t.append(int(element, base=base))

            return tuple(t)
        else:
            return data

    def getString(self, num, length, digits=False, upperalpha=False,
            loweralpha=True, unique=False, format="plain", rnd="new",
            headers=None, link="strings/"):
        """Interact with random.org string generator.

        @param num: The number of strings requested.
        @type num: int

        @param length: The length of the strings. All the strings produced will
            have the same length.
        @type length: int

        @param digits: Determines whether digits (0-9) are allowed to occur in
            the strings.
        @type digits: bool

        @param upperalpha: Determines whether uppercase alphabetic characters
            (A-Z) are allowed to occur in the strings.
        @type upperalpha: bool

        @param loweralpha: Determines lowercase alphabetic characters (a-z) are
            allowed to occur in the strings.
        @type loweralpha: bool

        @param unique: Determines whether the strings picked should be unique
            (as a series of raffle tickets drawn from a hat) or not (as a series of
            die rolls). If unique is set to True, then there is the additional
            constraint that the number of strings requested (num) must be less than
            or equal to the number of strings that exist with the selected length
            and characters.
        @type unique: bool
        
        @param format: Determines the return type of the document that the
            server produces as its response. If html is specified, the server
            produces a nicely formatted XHTML document (MIME type text/html),
            which will display well in a browser but which is somewhat
            cumbersome to parse. If plain is specified, the server produces as
            minimalistic document of type plain text (MIME type text/plain)
            document, which is easy to parse. If you are writing an automated
            client, you probably want to specify plain here.
        @type format: str

        @param rnd: Determines the randomization to use to generate the
            numbers. If new is specified, then a new randomization will created
            from the truly random bitstream at RANDOM.ORG. This is probably what
            you want in most cases. If id.identifier is specified, the identifier
            is used to determine the randomization in a deterministic fashion from
            a large pool of pregenerated random bits. Because the numbers are
            produced in a deterministic fashion, specifying an id basically uses
            RANDOM.ORG as a pseudo-random number generator. The third
            (date.iso-date) form is similar to the second; it allows the
            randomization to be based on one of the daily pregenerated files. This
            form must refer to one of the dates for which files exist, so it must
            be a day in the past. The date must be in ISO 8601  format (i.e.,
            YYYY-MM-DD).
        @type rnd: str

        @param headers: The HTTP headers to send. Passed to urllib2.Request()
            Defaults to None.
        @type headers: dict

        @param link: The relative link to the integers script.
        @type link: str
        
        @return: If format is "plain" a tuple of strings is returned, else the
            raw html page is returned.
        """

        if num > self.limits["maxNum"]:
            msg = "The number of strings is limited to %d"
            raise OverflowError, msg % self.limits["maxNum"]
        if length < self.limits["strMin"] or length > self.limits["strMax"]:
            msg = "Length must be between %d and %d"
            raise OverflowError, msg % (self.limits["strMin"],
                self.limits["strMax"])
        if format not in ("html", "plain"):
            raise TypeError, "Bad format"

        if headers is None:
            headers = self.headers

        if digits: digits = "on"
        else: digits = "off"

        if upperalpha: upperalpha = "on"
        else: upperalpha = "off"

        if loweralpha: loweralpha = "on"
        else: loweralpha = "off"

        if unique: unique = "on"
        else: unique = "off"


        uri = "/".join((self.uri, link))
        uri += "?num=%d&len=%d&digits=%s&upperalpha=%s&loweralpha=%s&unique=%s&format=%s&rnd=%s" % \
                (num, length, digits, upperalpha, loweralpha, unique, format,
                        rnd)

        data = getPage(uri, headers)
        
        if format == "plain":
            datalist = data.split(LF)
            datalist.remove('')

            return tuple(datalist)
        else:
            return data
    
    def quota(self, ip=None, format="plain", headers=None, link="quota/"):
        """Interact with random.org quota checker.

        @param ip: The IP address for which you wish to examine the quota. Each
            value for n should be an integer in the [0,255] interval. This
            parameter is optional. If you leave it out, it defaults to the IP
            address of the machine from which you are issuing the request.
        @type ip: str

        @param format: Determines the return type of the document that the
            server produces as its response. If html is specified, the server
            produces a nicely formatted XHTML document (MIME type text/html),
            which will display well in a browser but which is somewhat
            cumbersome to parse. If plain is specified, the server produces as
            minimalistic document of type plain text (MIME type text/plain)
            document, which is easy to parse. If you are writing an automated
            client, you probably want to specify plain here.
        @type format: str

        @param headers: The HTTP headers to send. Passed to urllib2.Request()
        @type headers: dict

        @param link: The relative link to the integers script.
        @type link: str
        
        @return: If format is "plain", then the quota is returned as an integer
            else the raw html page is returned.
        """


        if ip is not None:
            socket.inet_aton(ip) # will raise socket.error if ip is invalid.
        if format not in ("html", "plain"):
            raise TypeError, "Bad format"

        if headers is None:
            headers = self.headers

        uri = "/".join((self.uri, link)) + "?"
        if ip is not None:
            uri += "ip=" + ip + "&"
        uri += "format=" + format

        data = getPage(uri, headers)

        if format == "plain":
            data = int(data)

        return data

    def checkQuota(self, ip=None):
        """Check quota.

        @param ip: The IP address for which you wish to check the quota.
        @type ip: str

        @return: Returns False if quota is lower than 0 and True otherwise.
        """
        
        q = self.quota(ip, format="plain")
        if q < 0:
            return False
        return True

    # Old API
    def checkBuffer(self, headers=None, link="cgi-bin/checkbuf"):
        """Check random.org buffer.

        @param headers: The HTTP headers to send. Passed to urllib2.Request()
        @type headers: dict

        @param link: The relative link to the integers script.
        @type link: str

        @return: The value of buffer is returned as an integer.
        """
        uri = "/".join((self.uri, link))
        
        if headers is None:
            headers = self.headers
        
        data = getPage(uri, headers)
        return int(data.replace("%\n", ""))

    def getRandomNumber(self, num, minimum=-10e8, maximum=10e8, columns=5,
            headers=None, link="cgi-bin/randnum"):
        """Get a list of integers from randnum script.

        @param num: The number of integers requested.
        @type num: int

        @param minimum: The smallest value allowed for each integer.
        @type minimum: int

        @param maximum: The largest value allowed for each integer.
        @type maximum: int

        @param columns: The number of columns in which the integers will be arranged.
        @type columns: int

        @param headers: The HTTP headers to send. Passed to urllib2.Request()
        @type headers: dict

        @param link: The relative link to the integers script.
        @type link: str

        @return: A tuple of integers is returned.
        """
        warnings.warn("Use RandomOrg.getInteger(), getRandomNumber is deprecated.",
                DeprecationWarning, stacklevel=2)

        if num > self.limits["maxNum"]:
            msg = "The number of integers is limited to %d"
            raise OverflowError, msg % self.limits["maxNum"]
        if minimum < self.limits["intMin"]:
            msg = "The lower bound of the interval is limited to %d"
            raise OverflowError, msg % self.limits["intMin"]
        if maximum > self.limits["intMax"]:
            msg = "The upper bound of the interval is limited to %d"
            raise OverflowError, msg % self.limits["intMax"]
        if columns < self.limits["columnMin"] or columns > self.limits["columnMax"]:
            msg = "columns must be between %d and %d"
            raise OverflowError, msg % (self.limits["columnMin"],
                    self.limits["columnMax"])

        if headers is None:
            headers = self.headers

        uri = "/".join((self.uri, link)) +\
            "?num=%d&min=%d&max=%d&col=%d" % (num, minimum, maximum, columns)
        data = getPage(uri, headers)

        datalist = data.split(LF)
        datalist.remove('')

        t = []
        for element in datalist:
            if TAB in element:
                y = []
                for elem in element.split(TAB):
                    y.append(int(elem))
                t.append(tuple(y))
            else:
                t.append(int(element))

        return tuple(t)

    def getRandomByte(self, nbytes=256, format="f", headers=None,
            link="cgi-bin/randbyte"):
        """Get a number of raw bytes from randbyte script.

        @param nbytes: The number of bytes requested.
        @type nbytes: int

        @param format: The format in which the bytes are requested.
            Avaliable formats are 'f' for raw, 'h' for hexadecimal, 'd' for
            decimal, 'o' for octal and 'b' for binary.
        @type format: str

        @param headers: The HTTP headers to send. Passed to urllib2.Request()
        @type headers: dict

        @param link: The relative link to the randbyte script.
        @type link: str

        @return: A tuple of bytes received.
        """
                
        uri = "/".join((self.uri, link)) + "?nbytes=%d&format=%s" % (nbytes,
                format)

        if format not in ("f", "h", "d", "o", "b"):
            raise TypeError, "Bad format"

        if headers is None:
            headers = self.headers

        data = getPage(uri, headers)

        datalist = data.split(LF)
        
        return tuple(datalist)

    def getRandomSequence(self, minimum=-10e8, maximum=10e8, headers=None,
            link="cgi-bin/randseq"):
        """Get a randomized sequence of numbers from randseq script."""

        if minimum < -10e8:
            msg = "The lower bound of the interval is limited to -10e8"
            raise OverflowError, msg
        if maximum > 10e8:
            msg = "The upper bound of the interval is limited to 10e8"
            raise OverflowError, msg

        if headers is None:
            headers = self.headers

        uri = "/".join((self.uri, link)) + "?min=%d&max=%d" % (minimum, maximum)

        data = getPage(uri, headers)

        return data
