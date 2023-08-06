#!/usr/bin/env python

# Copyright (c) 2006-2008 Andrew Walkingshaw <andrew@lexical.org.uk>
# except XSLT components: copyright (c) 2005-2008 Toby White <tow@uszla.me.uk> 
#                 and (c) 2007-2008 Andrew Walkingshaw <andrew@lexical.org.uk>
#
# All rights reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR USE OF OTHER DEALINGS IN
# THE SOFTWARE.

from lxml import etree
import golem, sys, optparse, urllib2, StringIO, gzip, random
# set warning levels
golem.setTypeWarning(False)
golem.setDataWarning(True)

def make_parser():
    parser = optparse.OptionParser()
    parser.add_option("-d", "--dictionary", metavar="FILE",
                      dest="dictionaryfile", help="Dictionary filename")
    parser.add_option("-n", "--namespace", metavar="URI",
                      dest="dictionarynamespace", help="Dictionary namespace")
    return parser

def bind_print_rdf(a):
    """ Return a custom print_rdf_rich bound to a specific URL"""

    def print_rdf(x):
        return golem.helpers.stream.generics.print_rdf_rich(x, resource=a)
    return print_rdf

def getfile(url):
    """ Get a GZIPped file and return it as StringIO"""
    try:
        print >> sys.stderr, "Getting:", url
    except UnicodeEncodeError:
        print >> sys.stderr, "Unprintable URI: abandoning"
        raise 

    request = urllib2.Request(url)
    request.add_header('Accept-encoding', 'gzip')
    op = urllib2.build_opener()
    try:
        f = op.open(request)
        try:
            print >> sys.stderr, "Getting:", url
        except UnicodeEncodeError:
            print >> sys.stderr, "Unprintable URI: abandoning"
            raise 
    except urllib2.HTTPError:
        print >> sys.stderr, "404: ", url
        raise
    gzdata = StringIO.StringIO(f.read())
    try:
        decompressor = gzip.GzipFile(fileobj=gzdata)
        data = decompressor.read()
    except IOError:
        gzdata.seek(0)
        data = gzdata.read()
    return data

def rdfstring(uri, concepts_to_map, mapping):
    output = ""
    data = getfile(uri)
    map = {}        
    for c in concepts_to_map:
        map[c] = bind_print_rdf(uri)
    mapping.assign(map)
    stream = golem.helpers.stream.Stream(mapping)
    output += """<?xml version="1.0"?>
<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
         xmlns:golemrdf="http://www.lexical.org.uk/golem/RDF#">
"""
    output += stream.process(StringIO.StringIO(data))
    output += """
</rdf:RDF>"""
    return output

def main(*args, **kwargs):
    parser = make_parser()
    options, varargs = parser.parse_args()
    if len(varargs) > 1:
        print >> sys.stderr, "One URL at a time!"
        sys.exit(1)
    uri = varargs[0]
    
    mapping = golem.helpers.stream.Mapping(options.dictionaryfile,
                                           options.dictionarynamespace)
    concepts_to_map = [x.id for x in
                       mapping.dictionary.concept("absolute")\
                           .getAllImplementations() if x.id!="absolute"]

    print rdfstring(uri, concepts_to_map, mapping)

if __name__ == "__main__":
    main()
