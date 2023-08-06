#!/usr/bin/env python

# Part of pyGolem. See LICENSE in the root of your distribution for the license.
# Andrew Walkingshaw <andrew@lexical.org.uk>

import sys, pickle, golem, generics
from lxml import etree
import md5

class Mapping(dict, generics.ns_dict_mixin):
    def __init__(self, dictionaryfile, dictionarynamespace):
        self.dictionary = self.namespaced_dictionary(dictionaryfile,
                                                     dictionarynamespace)
        
    def assign(self, d):
        for key in d:
            self[key] = d[key]    

class Stream(object):
    def __init__(self, mappings):
        self.mappings = mappings # of class Mappings
        self.data = None
        self.cached_tree = None
        self.cached_tree_md5 = None
        
    def process(self, filename, onXML=False, onValues=True):
        # filename is a bit of a misnomer here: file-like objects are fine.
        try:
            fdata = filename.read()
            f = filename
        except AttributeError:
            f = open(filename, "r")
            fdata = f.read()
        md5sum = md5.new(fdata).hexdigest()
        if md5sum != self.cached_tree_md5:
            f.seek(0)
            tree = etree.parse(f)
            self.cached_tree = tree
            self.cached_tree_md5 = md5sum
        else:
            # same as the last file we saw, so we can save an etree reparse
            tree = self.cached_tree
        # find instances
        result = ""

        for key in self.mappings:
            address = key.split(",")
            processor = self.mappings[key]
            concepts=golem.db.conceptlist(
                *[self.mappings.dictionary.concept(c) for c in address])
            xpath = golem.helpers.xpath.xpath(concepts)
            # Clark form...
            sanitized_addr = address[-1].replace(":", "_")
            sanitized_addr = sanitized_addr.replace("/", "_over_")
            sanitized_addr = sanitized_addr.replace("\\", "_backslash_")
            sanitized_addr = sanitized_addr.replace("%", "_pct")
            namespace = self.mappings.dictionary.d.dnamespace
            if not (namespace.endswith("#") or namespace.endswith("/")):
                uri = "{%s#}%s" % (namespace, sanitized_addr)
            else:
                uri = "{%s}%s" % (namespace, sanitized_addr)
            class Result(list):
                __slots__ = ["filename", "uri"]
                def __init__(self, data, filename=None,
                             uri=None):
                    self.filename = filename
                    self.uri = uri
                    list.__init__(self, data)
                
            res = Result([], filename=filename, uri=uri)
            for x in xpath:
                nodes = tree.xpath(x, namespaces=golem.namespaces)
                res.extend(tree.xpath(
                            x, 
                            namespaces=golem.namespaces))
            # run processor
            if onXML:
                result += processor(res)
                result += "\n"
            elif onValues:
                try:
                    pres = Result([concepts[-1].getvalue(x) for x in res],
                                  filename = res.filename, uri = res.uri)
                    result += processor(pres)

                except AttributeError, e:
                    id = concepts[-1].id
                    print >> sys.stderr, "Skipping id", id, "- no assigned " \
                        "getvalue template in dictionary"
                except ValueError:
                    print >> sys.stderr, \
                        "Malformed data in %s - skipping."% concepts[-1].id
                
        self.result = result
        return result
