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
import golem

class RDFStream(object):
    """ Proxy for golem.helpers.stream.Stream:
    
    Requires maps like:
    
    {"concept1,concept2,concept3": http://namespace.of.datatype#uri,
    ...
    }
    """
    
    def __init__(self, dictionary, dictionarynamespace, map):
        funcmap = {}
        for conceptset in map:
            funcmap[conceptset] =\
                   lambda y, z=map[conceptset]: \
                   golem.helpers.stream.generics.print_rdf(y,datatype_uri=z)

        mapping = golem.helpers.stream.Mapping(dictionary,
                                               dictionarynamespace)
        mapping.assign(funcmap)
        self.__stream = golem.helpers.stream.Stream(mapping)

    def rdfheader(self):
        return """<?xml version="1.0"?>
<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
"""
    def rdffooter(self):
        return """
</rdf:RDF>"""        

    def process(self, filename):
        return self.__stream.process(filename)

    def batch(self, filenames):
        out = ""
        out += self.rdfheader()
        for fn in filenames:
            out += self.process(fn)
        out += self.rdffooter()
        return out
    
def castep_test(filenames, **kwargs):
    dictionaryfile = "castep.dump.xml"
    dnamespace = "http://www.materialsgrid.org/castep/dictionary"
    map = {"Etot": r"{http://cmlcomp.org/rdf/common#}total_energy",
           "task": r"{http://cmlcomp.org/rdf/common#}simulation_type"}
    
    processor = RDFStream(dictionaryfile, dnamespace, map)
    print processor.batch(filenames)
    
if __name__ == "__main__":
    import sys
    castep_test(sys.argv[1:])
