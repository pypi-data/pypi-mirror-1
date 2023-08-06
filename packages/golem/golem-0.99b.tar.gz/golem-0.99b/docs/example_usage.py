#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
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

import golem

#
# This is a very cut-down, and heavily commented, example of how to use
# golem to write a command-line query tool for your CML data. 
# bin/lexicographer.py is a much more fully-featured version of this idea,
# so if you need a tool, use that: but if you want to understand how 
# golem works, read this!
#
def test(term, filename):
    #
    """\
Find instances of a given dictionary term in a CML file.

term is the term we are going to search for. This will be something 
like 'Etot' (which you will know from elsewhere is the total energy of 
your code.) We are going to try and find all instances of any 
quantity within a document which answers the description of this term. 
    
"filename" is the file we are going to search. To know how to find 
these quantities in the documents, we'll need a dictionary (since a 
dictionary maps between terms and their definitions). We'll look for 
dictionaries in a default location (see below) or you can specify your 
own dictionary (also see below).
"""
    
    # Load in a dictionary, creating a golem dictionary object.
    # Dictionaries are loaded from ~/.cmldictionaries/ (on Unix or OS X)
    # or C:\cmldictionaries\ (on Windows). If you need to load a dictionary
    # from somewhere else, the best way to do it is:
    #
    # d = golem.Dictionary("/full/path/to/file")
    #
    d = golem.loadDictionary("castepDict.xml")
    #
    # Dictionaries have namespaces, which are URLs (web addresses); these
    # "name" the dictionaries - ie two dictionaries with different filenames
    # on your disc, but the same *namespace*, are about the same thing.
    #
    # You need to specify the namespace here. It'll be in the first few
    # lines of your dictionary if you don't know it already...
    #
    dnamespace = "http://www.materialsgrid.org/castep/dictionary"
    #
    # (as defined in the dictionary headers:
    # <dictionary 
    #   namespace="http://www.materialsgrid.org/castep/dictionary"
    #   dictionaryPrefix="castep" 
    #   title="CASTEP Dictionary" ...>
    #
    # golem Dictionary objects inherit from the Python _dictionary_ type,
    # and the entries in them are keyed by namespace and ID in the form:
    # {namespace}id.
    #
    # Here, we've defined the namespace up front, but the user's
    # supplied the term (which is the ID), so we need to construct
    # the key...
    #
    entry = d["{%s}%s" % (dnamespace, term)]
    #
    # so we've now got the entry. Now to look for all the places where 
    # this entry is found in a file - in other words, all the instances
    # of the concept we're looking for.
    # 
    # _entry.findin *always* returns a list_; if nothing's found, it's
    # just an empty one.
    #
    branches = entry.findin(filename)
    #
    # So now we need to loop over what we've found and do something with
    # it/them.
    #
    for branch in branches:
        #
        # entry.getvalue runs the "getvalue" XSLT template belonging to
        # the entry over the chunk of ElementTree you pass it.
        #
        # That template returns a two-element JSON list:
        #
        # [value, "units"]
        #
        # which is then loaded by the Golem library, giving you a
        # Python object back, with the value you'd expect and with      
        # value.unit set to "units".
        #
        # value.entry is set to point at the dictionary entry where
        # 'value' came from.
        #
        val = entry.getvalue(branch)
        # 
        # And print it out:
        #
        print val, "- units:", val.unit
        #
        # and check where it came from.
        #
        if val.entry == entry:
            print "Entries on value and from dictionary match."
        
if __name__ == "__main__":
    import sys
    #
    # Arguments: CASTEP dictionary term to look up and evaluate,
    #            file to look it up in.
    #
    test(sys.argv[1], sys.argv[2])
