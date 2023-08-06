# -*- coding: utf-8 -*-
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

'''\
The Golem ontology parsing library.

This module contains the main class which parses Golem/CML dictionaries, 
as defined by the CML and  Golem schemata, and allows you to use them to 
extract and convert information found in CML datafiles.
'''

from lxml import etree
from StringIO import StringIO
import sys, new, copy, os
import simplejson
from helpers.generics import golemdata

## module-level variables
version = "0.99beta"
data_warning = True
type_warning = True
# Our default namespace context for XPath expressions
namespaces = {
    "cml": "http://www.xml-cml.org/schema",
    "golem": "http://www.lexical.org.uk/golem",
    "h": "http://www.w3.org/1999/xhtml",
    "xsl": "http://www.w3.org/1999/XSL/Transform",
    "xsd": "http://www.w3.org/2001/XMLSchema"
    }

namespaces_full = {
    None: "http://www.xml-cml.org/schema",
    "cml": "http://www.xml-cml.org/schema",
    "golem": "http://www.lexical.org.uk/golem",
    "h": "http://www.w3.org/1999/xhtml",
    "xsl": "http://www.w3.org/1999/XSL/Transform",
    "xsd": "http://www.w3.org/2001/XMLSchema"
    }


def setDataWarning(val):
    """\
Set whether warnings will be emitted when unit/type-bearing data is modified.

Default is True."""

    global data_warning
    data_warning = val

def setTypeWarning(val):
    """\
Set whether warnings will be emitted when a dictionary Entry without 
a defined type is used.

Default is True."""

    global type_warning
    type_warning = val

# Where should we look for dictionaries by default?
# they live in $installdir/dictionaries
# we are in $installdir/golem - or an egg
try:
    # Well, if we have setuptools available, we can ask it
    from pkg_resources import resource_listdir, resource_stream
    data_dir = ("egg",)
except ImportError:
    data_dir = ("file", os.path.join(os.path.dirname(__file__), ".."))

def _getDefaultDictionaries():
    """Return a list of file-like objects that can be fed
    to a dictionary loader. This is different according
    to whether we are running from an egg or a file."""
    files = []
    if data_dir[0] == "egg":
        for f in resource_listdir(__name__, "../dictionaries"):
            if f.endswith(".xml"):
                files.append(resource_stream(__name__, "../dictionaries/"+f))
    else:
        dict_dir = os.path.join(data_dir[1], "dictionaries")
        for f in os.listdir(dict_dir):
            if f.endswith(".xml"):
                files.append(open(os.path.join(dict_dir, f)))
    return files


class GXpath(object):
    def __init__(self, xqnode):
        self.path = xqnode.text
    

class ImpOnlyEntry(object):
    '''\
Dictionary helper class: this is used to store information on entries
which have been pointed to (by, say, <golem:implements>), but which haven't
themselves been parsed yet.
'''
    def __init__(self):
        self.ImplementedBy = []
        self.SeeAlso = []
        self.Synonyms = []
        self.Children = []
        self.defer = {}


class EntryCollection(dict):
    def __init__(self, asModel=False, default=False):
        """ If asked, we'll load up this EntryCollection
        with all the installed dictionaries """
        self.asModel = asModel
        if default:
            for f in _getDefaultDictionaries():
                self.add_entries_from_file(f)
                f.close()

    def add_entries_from_etree(self, ns, el):
        """ This takes a string, ns, denoting namespace, and 
        an ElementTree nodelist, ns, of <cml:entry> elements,
        and organizes them all."""      
        for entry in el:
            # We store Dictionary entries keyed by what amounts to Clark form.
            e = Entry(d=self, ns=ns, xml=entry, asModel=self.asModel)
            key = "{%s}%s" % (ns, e.id)
            if not key in self:
                self[key] = e
            else:
                # pull the implementations which have been set before
                # ditto for synonyms
                ib = e.ImplementedBy
                sy = e.Synonyms
                ch = e.Children

                for i in self[key].ImplementedBy:
                    if i not in ib:
                        ib.append(i)
                for i in self[key].Synonyms:
                    if i not in sy:
                        sy.append(i)
                for i in self[key].Children:                    
                    if i not in ch:
                        ch.append(i)

                # now switch from pointing at the ImpOnlyEntry to the real
                # entry...
                e.ImplementedBy = ib
                e.Synonyms = sy
                e.Children = ch
                self[key] = e

            # set up ImpOnlyEntries for entries we haven't got to yet

            # and store the ImplementedBys...
            for k in e.imps:
                if k not in self:
                    self[k] = ImpOnlyEntry()
                self[k].ImplementedBy.append(key)
            # and children...
            for k in e.childOf:
                if k not in self:
                    self[k] = ImpOnlyEntry()
                self[k].Children.append(key)

            # We need to do something similar to sanity-check synonyms, 
            # too. We make the assumption that *all synonyms are valid
            # and bidirectional*, even if not specified in both directions:
            # also, if A->B and B<->C then A<->C, and we check for that.
            # For SeeAlsos, we don't do anything - letting them dangle is
            # just fine, we can catch the exception (if there is one!) later
            # because they're not designed to be generically 
            # machine-processable in any case - the semantics are undefined,
            # so they can be used to implement other relationships.

            synset = [key] # everything is its own synonym!
            visited = [key]

            for k in e.Synonyms:
                if k not in self:
                    self[k] = ImpOnlyEntry()
                
            synset.extend(e.Synonyms)
            while True:
                newsynonyms = []
                for key in synset:
                    if key not in visited:
                        for synonym in self[key].Synonyms:
                            if synonym not in synset \
                                    and synonym not in newsynonyms: 
                                newsynonyms.append(synonym)
                        visited.append(key)
                synset.extend(newsynonyms)
                visited.sort(); synset.sort()
                # if we've visited every key in our set then we have
                # a self-consistent view of synonym space, so we can stop
                if synset == visited:
                    break
            # so we can assign this list of visited nodes to be the set
            # of synonyms for each node...
            for key in visited:
                self[key].Synonyms = copy.copy(visited)
                # and remove ourself.
                self[key].Synonyms.remove(key)

    def add_entries_from_file(self, f):
        """ This will take a filename or filehandle, f; parse
        it as an XML document, extract all CML dictionaries
        and add their entries to the collection."""
        tree = etree.parse(f)
        dnodes = tree.xpath("//cml:dictionary", namespaces=namespaces)
        for d in dnodes:
            ns = d.get("namespace")
            el = d.xpath("cml:entry", namespaces=namespaces)

            self.add_entries_from_etree(ns, el)

        self.resolve_entry_templates()

    def resolve_entry_templates(self):
        """ Here we run over all entries, to check if any are
        deferring template calling elsewhere. We resolve any dangling
        references. The referent of such references MUST exist in
        the dictionary, or we throw an error """
        for k in self.keys():
            for (r, b, i) in self[k].defer.keys():
                ct = self[k].defer[(r, b, i)]
                try:
                    t = self[ct].templates[(r, b, i)]
                    self[k].templates[(r, b, i)] = t
                    self[k].sort_out_binding(r, b, i, t)
                    del self[k].defer[(r, b, i)]
                except KeyError:
                    print >> sys.stderr, "Missing template in dictionary"
                    sys.exit(1)


class Dictionary(EntryCollection):
    '''\
Main class for representing CML/Golem dictionaries.

Example of usage:
    
>>> from StringIO import StringIO
>>> dictionarystring = """<?xml version="1.0"?>
... <dictionary 
...   namespace="http://www.materialsgrid.org/castep/dictionary"
...   dictionaryPrefix="castep" 
...   title="CASTEP Dictionary"
...   xmlns="http://www.xml-cml.org/schema"
...   xmlns:h="http://www.w3.org/1999/xhtml/"
...   xmlns:cml="http://www.xml-cml.org/schema"
...   xmlns:xsd="http://www.w3.org/2001/XMLSchema"
...   xmlns:golem="http://www.lexical.org.uk/golem"
...   xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
...   <entry id="xcFunctional" term="Exchange-Correlation Functional">
...     <annotation />
...     <definition>
...       The exchange-correlation functional used.
...     </definition>
...     <description>
...      <h:div class="dictDescription">
...         Available values for this are:
...         <h:ul>
...           <h:li>
...             <h:strong>LDA</h:strong>
...             , the Local Density Approximation
...           </h:li>
...           <h:li>
...             <h:strong>PW91</h:strong>
...             , Perdew and Wang's 1991 formulation
...           </h:li>
...           <h:li>
...             <h:strong>PBE</h:strong>
...             Perdew, Burke and Enzerhof's original GGA
...             functional
...           </h:li>
...           <h:li>
...             <h:strong>RPBE</h:strong>
...             , Hammer et al's revised PBE functional
...           </h:li>
...         </h:ul>
...       </h:div>
...     </description>
...     
...     <metadataList>
...       <metadata name="dc:author" content="golem-kiln" />
...     </metadataList>
...     <golem:xpath>/cml:cml/cml:parameterList[@dictRef="input"]/cml:parameter[@dictRef="castep:xcFunctional"]</golem:xpath>
...     <golem:template call="scalar" role="getvalue" binding="pygolem_serialization" />
...     <golem:template role="arb_to_input" binding="input" input="external">
...       <xsl:stylesheet version='1.0' 
...                       xmlns:xsl='http://www.w3.org/1999/XSL/Transform'
...                       xmlns:cml='http://www.xml-cml.org/schema'>
...         <xsl:strip-space elements="*" />
...         <xsl:output method="text" />
...         <xsl:param name="p1" />
...         <xsl:template match="/">
...           <xsl:text>XC_FUNCTIONAL </xsl:text><xsl:value-of select="$p1" />      
...   </xsl:template>
...       </xsl:stylesheet>
...     </golem:template>
...     <golem:implements>convertibleToInput</golem:implements>
...     <golem:implements>value</golem:implements>
...     <golem:implements>absolute</golem:implements>
...     <golem:childOf>input</golem:childOf>
... 
...     <golem:possibleValues type="string">
...       <golem:enumeration>
...         <golem:value>LDA</golem:value>
...         <golem:value>PW91</golem:value>
...         <golem:value>PBE</golem:value>
...         <golem:value>RPBE</golem:value>
...         <golem:value>HF</golem:value>
...         <golem:value>SHF</golem:value>
...         <golem:value>EXX</golem:value>
...         <golem:value>SX</golem:value>
...         <golem:value>ZERO</golem:value>
...         <golem:value>HF-LDA</golem:value>
...         <golem:value>SHF-LDA</golem:value>
...         <golem:value>EXX-LDA</golem:value>
...         <golem:value>SX-LDA</golem:value>
...       </golem:enumeration>
...     </golem:possibleValues>
...   </entry>
... 
... <entry id="scalar" term="Scalar default call">
...     <annotation />
...     <definition />
...     <description />
...     <metadataList />
...     <golem:template role="getvalue" binding="pygolem_serialization">
...         <xsl:stylesheet version='1.0' 
...                 xmlns:xsl='http://www.w3.org/1999/XSL/Transform'
...                 xmlns:cml='http://www.xml-cml.org/schema'
...                 xmlns:str="http://exslt.org/strings"
...                 xmlns:func="http://exslt.org/functions"
...                 xmlns:exsl="http://exslt.org/common"
...                 xmlns:tohw="http://www.uszla.me.uk/xsl/1.0/functions"
...                 extension-element-prefixes="func exsl tohw str"
...                 exclude-result-prefixes="exsl func tohw xsl str">
...         <xsl:output method="text" />
...   
...   
...   <func:function name="tohw:isAListOfDigits">
...     <!-- look only for [0-9]+ -->
...     <xsl:param name="x_"/>
...     <xsl:variable name="x" select="normalize-space($x_)"/>
...     <xsl:choose>
...       <xsl:when test="string-length($x)=0">
...         <func:result select="false()"/>
...       </xsl:when>
...       <xsl:when test="substring($x, 1, 1)='0' or
...                       substring($x, 1, 1)='1' or
...                       substring($x, 1, 1)='2' or
...                       substring($x, 1, 1)='3' or
...                       substring($x, 1, 1)='4' or
...                       substring($x, 1, 1)='5' or
...                       substring($x, 1, 1)='6' or
...                       substring($x, 1, 1)='7' or
...                       substring($x, 1, 1)='8' or
...                       substring($x, 1, 1)='9'">
...         <xsl:choose>
...           <xsl:when test="string-length($x)=1">
...             <func:result select="true()"/>
...           </xsl:when>
...           <xsl:otherwise>
...             <func:result select="tohw:isAListOfDigits(substring($x, 2))"/>
...           </xsl:otherwise>
...         </xsl:choose>
...       </xsl:when>
...       <xsl:otherwise>
...         <func:result select="false()"/>
...       </xsl:otherwise>
...     </xsl:choose>
...   </func:function>
... 
...   <func:function name="tohw:isAnInteger">
...     <!-- numbers fitting [\+-][0-9]+ -->
...     <xsl:param name="x_"/>
...     <xsl:variable name="x" select="normalize-space($x_)"/>
...     <xsl:variable name="try">
...       <xsl:choose>
...         <xsl:when test="starts-with($x, '+')">
...           <xsl:value-of select="substring($x,2)"/>
...         </xsl:when>
...         <xsl:when test="starts-with($x, '-')">
...           <xsl:value-of select="substring($x,2)"/>
...         </xsl:when>
...         <xsl:otherwise>
...           <xsl:value-of select="$x"/>
...         </xsl:otherwise>
...       </xsl:choose>
...     </xsl:variable>
...     <func:result select="tohw:isAListOfDigits($try)"/>
...   </func:function>
... 
...   <func:function name="tohw:isANumberWithoutExponent">
...     <!-- numbers fitting [\+-][0-9]+(\.[0-9]*) -->
...     <xsl:param name="x"/>
...     <xsl:choose>
...       <xsl:when test="contains($x, '.')">
...         <func:result select="tohw:isAnInteger(substring-before($x, '.')) and
...                              tohw:isAListOfDigits(substring-after($x, '.'))"/>
...       </xsl:when>
...       <xsl:otherwise>
...         <func:result select="tohw:isAnInteger($x)"/>
...       </xsl:otherwise>
...     </xsl:choose>
...   </func:function>
... 
...   <func:function name="tohw:isAnFPNumber">
...     <!-- Try and interpret a string as an exponential number -->
...     <!-- should only recognise strings of the form: [\+-][0-9]*\.[0-9]*([DdEe][+-][0-9]+)? -->
...     <xsl:param name="x"/>
...     <xsl:choose>
...       <xsl:when test="contains($x, 'd')">
...         <func:result select="tohw:isANumberWithoutExponent(substring-before($x, 'd')) and
...                              tohw:isAnInteger(substring-after($x, 'd'))"/>
...       </xsl:when>
...       <xsl:when test="contains($x, 'D')">
...         <func:result select="tohw:isANumberWithoutExponent(substring-before($x, 'D')) and
...                              tohw:isAnInteger(substring-after($x, 'D'))"/>
...       </xsl:when>
...       <xsl:when test="contains($x, 'e')">
...         <func:result select="tohw:isANumberWithoutExponent(substring-before($x, 'e')) and
...                              tohw:isAnInteger(substring-after($x, 'e'))"/>
...       </xsl:when>
...       <xsl:when test="contains($x, 'E')">
...         <func:result select="tohw:isANumberWithoutExponent(substring-before($x, 'E')) and
...                              tohw:isAnInteger(substring-after($x, 'E'))"/>
...       </xsl:when>
...       <xsl:otherwise>
...          <func:result select="tohw:isANumberWithoutExponent($x)"/>
...       </xsl:otherwise>
...     </xsl:choose>
...   </func:function>
...         
...   <xsl:template match="/">
...     <xsl:apply-templates />
...   </xsl:template>
...     
...   <xsl:template match="cml:scalar">
...     <xsl:variable name="value">
...       <xsl:choose>
...         <xsl:when test="tohw:isAnFPNumber(.)">
...           <xsl:value-of select="." />
...         </xsl:when>
...         <xsl:otherwise>
...           <xsl:text>"</xsl:text><xsl:value-of select="." /><xsl:text>"</xsl:text>
...         </xsl:otherwise>
...       </xsl:choose>
...     </xsl:variable>
...     <xsl:variable name="units">
...       <xsl:choose>
...         <xsl:when test="@units">
...           <xsl:text>"</xsl:text><xsl:value-of select="@units" /><xsl:text>"</xsl:text>
...         </xsl:when>
...         <xsl:otherwise>
...           <xsl:text>""</xsl:text>
...         </xsl:otherwise>
...       </xsl:choose>
...     </xsl:variable>
...     <xsl:text>[</xsl:text><xsl:value-of select="$value"/><xsl:text>,</xsl:text><xsl:value-of select="$units" /><xsl:text>]</xsl:text>
...   </xsl:template>
... </xsl:stylesheet>
...     </golem:template>
... 
...     <golem:template role="defaultoutput">
...       <xsl:stylesheet version='1.0' 
...                       xmlns:xsl='http://www.w3.org/1999/XSL/Transform'
...                       xmlns:cml='http://www.xml-cml.org/schema'
...                       xmlns:str="http://exslt.org/strings"
...                       extension-element-prefixes="str"
...                       >
...         <xsl:output method="text" />
...         <xsl:param name="name" />
...         <xsl:param name="value" />
...         <xsl:template match="/">
...           <xsl:value-of select='$name' /><xsl:value-of select='$value' />
...         </xsl:template>
...       </xsl:stylesheet>
...     </golem:template>
...     <golem:seealso>gwtsystem</golem:seealso>
...   </entry>
... </dictionary>
... """
>>> d = Dictionary(StringIO(dictionarystring))
>>> xcf = d["{http://www.materialsgrid.org/castep/dictionary}xcFunctional"]
>>> cmlstr = """<?xml version="1.0" encoding="UTF-8"?>
... <?xml-stylesheet href="display.xsl" type="text/xsl"?>
... <cml convention="FoX_wcml-2.0" fileId="NaCl_00GPa.xml" version="2.4"
...   xmlns="http://www.xml-cml.org/schema"
...   xmlns:castep="http://www.materialsgrid.org/castep/dictionary"
...   xmlns:castepunits="http://www.materialsgrid.org/castep/units"
...   xmlns:cml="http://www.xml-cml.org/dict/cmlDict"
...   xmlns:xsd="http://www.w3.org/2001/XMLSchema"
...   xmlns:dc="http://purl.org/dc/elements/1.1/title"
...   xmlns:units="http://www.uszla.me.uk/FoX/units"
...   xmlns:atomicUnits="http://www.xml-cml.org/units/atomic">
...   <metadataList title="Autocaptured metadata">
...     <metadata name="dc:date" content="2007-02-09"/>
...   </metadataList>
...   <parameterList dictRef="input" convention="Input Parameters">
...     <parameter dictRef="castep:xcFunctional"
...       name="Exchange-Correlation Functional">
...       <scalar dataType="xsd:string">PBE</scalar>
...     </parameter>
...   </parameterList>
... </cml>
... """
>>> tree = etree.parse(StringIO(cmlstr))
>>> xcfd = xcf.findin(tree)
>>> print len(xcfd)
1
>>> xcval = xcf.getvalue(xcfd[0])
>>> print xcf.getvalue(xcfd[0])
PBE
>>> # units are not defined on XCFunctional, so:
>>> print xcval.unit
golem:undefined
>>> # by convention
>>> print xcval.entry.definition
<BLANKLINE>
      The exchange-correlation functional used.
<BLANKLINE>
'''
    
    def __init__(self, filename=None, asModel=False):
        if filename:
            self.parsexml(filename, asModel=asModel)
    
    def parsexml(self, filename, asModel=False):
        """ Load and parse a CML dictionary."""

        self.asModel = asModel

        #load and parse the XML of the dictionary
        tree = etree.parse(filename)
        dnode = tree.xpath("/cml:dictionary", namespaces=namespaces)[0]
        self.title = dnode.get("title")

        #get this dictionary's namespace
        self.dnamespace = dnode.get("namespace")

        #now we need to iterate over dictionary entries, so we 
        #set up an iterator based on the XPath expression;
        el = dnode.xpath("cml:entry", namespaces=namespaces)

        self.add_entries_from_etree(self.dnamespace, el)

        self.resolve_entry_templates()

    def serialize(self, ordering=None):
        """ Serialize a dictionary back to XML. """
        root = etree.Element('dictionary', {
                "namespace": self.dnamespace 
                },
                nsmap = {
                None: "http://www.xml-cml.org/schema",
                "cml": "http://www.xml-cml.org/schema",
                "golem": "http://www.lexical.org.uk/golem",
                "h": "http://www.w3.org/1999/xhtml",
                "xsl": "http://www.w3.org/1999/XSL/Transform",
                "xsd": "http://www.w3.org/2001/XMLSchema"
                })
        mdlist = etree.SubElement(root, 'metadataList')
        metadata = etree.SubElement(mdlist, 'metaData',
                                    name="dc:creator", 
                                    content="golem-kiln")
        # and add the entries
        if not ordering:
            for key in self:
                root.append(self[key].serialize())
        if ordering:
            for key in etree.parse(ordering).xpath("cml:entry/@id", namespaces=namespaces):
                root.append(self["{%s}%s" % (self.dnamespace, key)].serialize())
        return etree.ElementTree(root)


class Entry(object):
    """\
The Entry class represents an entry in a Golem/CML dictionary.

Entries have the following structure.
   <entry id="template" term="Template entry">
     <annotation>
       <appinfo><!-- CML-specific machine-processable information --></appinfo>
     </annotation>
     <definition>Human-readable one-liner definition</definition>
     <description>Substantial human-readable documentation</description>
     <metadataList><!-- Dublin Core semantics -->
       <metadata name="dc:creator" content="Test Author" />
     </metadataList>
     <golem:xpath></golem:xpath>
     <golem:template role="role" binding="binding"> <!-- and optionally "@input" -->
     </golem:template>
     <golem:possibleValues type="DATATYPE">
       <golem:range>
         <golem:minimum>1</golem:minimum>
         <golem:maximum>100</golem:maximum>
       </golem:range>
       <!-- or -->
       <golem:enumeration>
         <golem:value>1</golem:value>
         <golem:value>2</golem:value>
         <golem:value>3</golem:value>
       </golem:enumeration>
     </golem:possibleValues> <!-- or matrix ... -->
     <golem:implements>otherEntry</golem:implements> <!-- times n -->
     <golem:synonym>synonymousEntry</golem:synonym> <!-- times n -->
     <golem:seealso>similarEntry</golem:seealso> <!-- times n -->
     <golem:childOf>parentEntry</golem:childOf> <!-- times n -->
   </entry>
"""
    def __init__(self, d, ns, xml=None, asModel=False):
        self.parentdictionary = d
        self.namespace = ns
        if xml is not None:
            self.parsexml(xml, asModel=asModel)

    def parsexml(self, x, asModel=False):
        """\
Load a dictionary entry from its XML representation. 

arguments: (etree for the entry, parent dictionary object).

Set asModel to true if you're using this dictionary as a model
for building a new one: it stashes way more of the native XML in that
case, allowing you to serialize it out directly into your new dictionary.
At present, this is only used by the dictionary generator
(bin/make_dictionary.py in your Golem distribution.)"""

# Brace yourselves...
#
# So if you look at this class's doctring, you can see what we need to 
# parse here. Thankfully, this isn't too hard... just very, very longwinded.
#
# Tag by tag:
# Annotation: discard for now. We're encoding what we need in the golem:
# namespace.
# Definition; string. Description; store the tree, it's HTML mostly.
# Templates; dictionary, but store each tree by key; it's an XSL
# transform.
# Relations (implements, synonym, seeAlso, childOf) - store.
# (Implements we have to be a bit canny with: we store the Implements
# relationships, but we really want Implemented By - so we stash those
# as well.)

        self.id = x.get("id")
        self.term = x.get("term")
        try:
            self.definition = x.xpath("./cml:definition", 
                                       namespaces=namespaces)[0].text
        except IndexError:
            self.definition = ""
        try:
            self.description = x.xpath("./cml:description", 
                                       namespaces=namespaces)[0]
        except IndexError:
            self.description = ""
        self.imps = []
        self.ImplementedBy = []
        self.Synonyms = []
        self.SeeAlso = []
        self.childOf = []
        self.Children = []

        # These are, in some sense, ordered by importance.
        # The more important, the further up the list (so an exception
        # doesn't chuck useful information...)
        
        # Build the implementation tree.
        # The Dictionary constructor puts the backlinks (which are the
        # important ones if we're walking the tree from the top down)
        # in.
        imp = x.xpath("golem:implements", namespaces=namespaces)
        for i in imp:
            try:
                namespace = i.get("namespace").strip()
            except:
                namespace = self.namespace
            if i.text is not None:
                c = "{%s}%s" % (namespace, i.text.strip())
                self.imps.append(c)

        childOf = x.xpath("golem:childOf", namespaces=namespaces)
        for i in childOf:
            try:
                namespace = i.get("namespace").strip()
            except:
                namespace = self.namespace
            if i.text is not None:
                c = "{%s}%s" % (namespace, i.text.strip())
                self.childOf.append(c)

        # seealso is easy: we just store the URIs.
        seealsos = x.xpath("golem:seealso", namespaces=namespaces)
        for i in seealsos:
            try:
                namespace = i.get("namespace").strip()
            except:
                namespace = self.namespace
            if i.text is not None:
                c = "{%s}%s" % (namespace, i.text.strip())
                self.SeeAlso.append(c)

        synonyms = x.xpath("golem:synonym", namespaces=namespaces)
        for i in synonyms:
            try:
                namespace = i.get("namespace").strip()
            except:
                namespace = self.namespace
            if i.text is not None:
                c = "{%s}%s" % (namespace, i.text.strip())
                self.Synonyms.append(c)

        gxpath = x.xpath("./golem:xpath", namespaces=namespaces)
        if len(gxpath):
            self.gxpath = GXpath(gxpath[0])

        possibleValues = x.xpath("golem:possibleValues", namespaces=namespaces)
        if len(possibleValues): 
            p = possibleValues[0]
            if asModel:
                self.pvxml = p # worth stashing for model case

            tr = p.xpath("golem:range", namespaces=namespaces)
#           print self.id, tr

            # get type of possibleValues
            stype = p.get("type")
            if stype:
                t_type = stype.strip()
                if t_type == "int": 
                    self.type = int
                    self.rep_type = "int"
                elif t_type == "float":
                    self.type = float
                    self.rep_type = "float"
                elif t_type == "string":
                    self.type = str
                    self.rep_type = "string"
                elif t_type == "matrix":
                    self.type = "matrix"
                    self.rep_type = "matrix"
                    arr = p.xpath("golem:matrix", namespaces=namespaces)[0]
                    self.dimensionx = int(arr.get("dimensionx"))
                    self.dimensiony = int(arr.get("dimensiony"))
                    if arr.get("type"):
                        a_type = arr.get("type").strip()
                    else:
                        a_type = None
                    self.rep_atype = a_type
                    if a_type == "int":
                        self.atype = int
                    elif a_type == "float":
                        self.atype = float
                    symm = arr.get("symmetric").strip()
                    if symm == "true":
                        self.symmetric = True
                    else:
                        self.symmetric = False
            else:
                self.type = str


            if tr: 
                r = tr[0]
#               print "test", r, self.id
                if len(r):
                    min = r.xpath("golem:minimum", namespaces=namespaces)
                    max = r.xpath("golem:maximum", namespaces=namespaces)
                    if len(min):
                        try:
                            if self.type == "matrix":
                                self.minimum = self.atype(min[0].text)
                            else:
                                self.minimum = self.type(min[0].text)
                        except ValueError:
                            print >> sys.stderr, \
                              "ValueError in golem:minimum:", \
                              max[0].text, max[0], \
                              [etree.tostring(x) for x in max]
                            sys.exit(1)
                    else:
                        self.minimum = None
                    if len(max):
                        try:
                            if self.type == "matrix":
                                self.maximum = self.atype(max[0].text)
                            else:
                                self.maximum = self.type(max[0].text)
                        except ValueError:
                            print >> sys.stderr, \
                              "ValueError in golem:maximum:", \
                              max[0].text, max[0], \
                              [etree.tostring(x) for x in max]
                            sys.exit(1)
                    else:
                        self.maximum = None
            else:
                self.possibleValues = []
                vals = p.xpath("./golem:enumeration", namespaces=namespaces)
                if vals:
                    for val in vals[0].xpath("golem:value", namespaces=namespaces):
                        self.possibleValues.append(self.type(val.text))
                        
        self.txml = {}
        self.templates = {}
        self.defer = {}
        for t in x.xpath("./golem:template", namespaces=namespaces):
            try:
                role = t.get("role")
                # you *have* to get role first, because it's only then
                # we can macro-substitute in the other template...
                call = t.get("call")
                ns = t.get("namespace")
                if not ns:
                    ns = self.namespace
                binding = t.get("binding")
                self.txml[(role, binding)] = t
                input = t.get("input")
                if call == None:
                    template = t.xpath("xsl:stylesheet", namespaces=namespaces)[0]
                    self.templates[(role, binding, input)] = template
                    self.sort_out_binding(role, binding, input, template)
                else:
                    # Note that we need to fill in the blanks later.
                    self.defer[(role, binding, input)] = "{%s}%s" % (self.namespace, call)

            except IndexError:
                pass

    def sort_out_binding(self, role, binding, input, template, newself=None):
        # We may end up calling this in order to bind the templates to
        # a second entry. If so, that entry will be passed in in newself
        if not newself: newself=self
        if binding == "pygolem_serialization":
            # we've got a 'getvalue', JSON-returning, template
            # create a closure with the template value in
            def getvalue(newself, cml, template=template):
                intrans = etree.XSLT(template)
                
                # Using this - WARNING - noncompliant JSON reader
                # because 'eval' isn't safe
                try:
                    # Here we want to allow both EntryInstance and ElementTree accesses:
                    try:
                        data = str(intrans(cml))
                    except TypeError:
                        data = str(intrans(cml.tree))
                    try:
                        struc = simplejson.loads(data)
                    except ValueError:                                
                        # escape errant backslashes
                        data = data.replace("\\", "\\\\")
                        struc = simplejson.loads(data)
                    # and typecheck this!
                except ValueError:
                    print >> sys.stderr, "exiting: ", str(data)
                    sys.stderr.write(
                        "JSON parsing of %s failed: exiting\n"
                        % etree.tostring(cml.tree))
                    raise ValueError
                if (isinstance(struc[1], basestring)):
                    # then the second element of the array is a
                    # units declaration, thus signifying we have
                    # solely one data/units pair here
                    struc = golemdata(struc[0], struc[1], self)
                else:
                    # otherwise, we have a list of data/unit pairs
                    struc = [golemdata(x[0], u=x[1]) for x in struc]
                    # and add the dictionary entry to the whole
                    # kit and caboodle...
                    struc = golemdata(struc, e=self)
                if isinstance(struc, list):
                    try:
                        self.matrix_shapecheck(struc)
                    except ValueError:
                        # we haven't got a matrix of the right shape
                        # but we might have a list of the right length
                        # to coerce, which is also acceptable.
                        # The reason we need this is because a list
                        # is the primary CML representation of a matrix
                        # and turning it into something like JSON 
                        # using XSLT is sometimes tricky.

                        struc = self.matrix_coercelist(struc)
                else:
                    try:
                        self.boundscheck(struc)
                    except TypeError:
                        print >> sys.stderr, 'Type check failed', struc
                        return None
                    except ValueError:
                        print >> sys.stderr, 'VType check failed', struc
                        return None
                return struc

            setattr(newself, role, new.instancemethod(getvalue, newself, Entry))

        elif binding == "input" and input == "external":
        #if role != "to_value" and role != "cml_to_input":
            try:
                def dyn(cls, arb, template=template):
                    return cls.dcall(template, arb)
                # create an instance method
                dm = new.instancemethod(dyn, self, Entry)
                # and save it
                setattr(self, role, dm)
            except IndexError:
                print >> sys.stderr, "Skipping empty template."


        # we need to special-case these two methods, which
        # is a little unsatisfying.
        # can we avoid this?
        elif binding == None:
            # the named arguments here are to create closures.
            # looks a bit weird but it's python idiom
            def cml_to_xml(self, cml, template=template):
                intrans = etree.XSLT(template)
                return intrans(cml)
            setattr(self, role, new.instancemethod(cml_to_xml, self, Entry))


    def serialize(self):
        """\
Write out this dictionary entry as XML.
"""

        namespace = self.namespace

        # entry, definition, description
        entry = etree.Element("entry", id=self.id, term=self.term)
        definition = etree.SubElement(entry, 'definition')
        if isinstance(self.definition, basestring):
            definition.text = self.definition
        elif self.definition == None:
            definition.text = ""
        else:
            definition.append(self.definition)
        if isinstance(self.description, basestring):
            desc = etree.SubElement(entry, "definition")
            desc.text = self.description
        else:
            entry.append(self.description)

        # golem:implements
        for i in self.imps:
            ns, term = i[1:].split("}")
            if ns == namespace:
                imp = etree.SubElement(entry, '{http://www.lexical.org.uk/golem}implements')
                imp.text = term
            else:
                imp = etree.SubElement(entry, '{http://www.lexical.org.uk/golem}implements', namespace=ns)
                imp.text = term

        # {http://www.lexical.org.uk/golem}seealso
        for a in self.SeeAlso:
            ns, term = a[1:].split("}")
            if ns == namespace:
                also = etree.SubElement(entry, '{http://www.lexical.org.uk/golem}seealso')
                also.text = term
            else:
                also = etree.SubElement(entry, '{http://www.lexical.org.uk/golem}seealso', namespace=ns)
                also.text = term

        # golem:synonym
        for s in self.Synonyms:
            ns, term = s[1:].split("}")
            if ns == namespace:
                syn = etree.SubElement(entry, '{http://www.lexical.org.uk/golem}synonym')
                syn.text = term
            else:
                syn = etree.SubElement(entry, '{http://www.lexical.org.uk/golem}synonym', namespace=ns)
                syn.text = term
        if hasattr(self, 'gxpath'):
            xp = etree.SubElement(entry, '{http://www.lexical.org.uk/golem}xpath')
            xp.text = self.gxpath.path

        # Now for golem:possibleValues.
        # first up - is there a type declaration?
        if hasattr(self, 'type'):
            if self.type is int:
                pv = etree.SubElement(entry, '{http://www.lexical.org.uk/golem}possibleValues', 
                                      type="int")
            if self.type is float:
                pv = etree.SubElement(entry, '{http://www.lexical.org.uk/golem}possibleValues', 
                                      type="float")
            if self.type is str:
                pv = etree.SubElement(entry, '{http://www.lexical.org.uk/golem}possibleValues', 
                                      type="string")
            if self.type == 'matrix':
                if hasattr(self, "atype"):
                    if self.atype is int:
                        at = "int"
                    elif self.atype is float:
                        at = "float"
                else:
                    at = None
                if self.symmetric:
                    symm = "true"
                else:
                    symm = "false"
                pv = etree.SubElement(entry, '{http://www.lexical.org.uk/golem}possibleValues', 
                                      type="matrix")
                mxargs = {"symmetric": symm,
                          "dimensionx": str(self.dimensionx), 
                          "dimensiony": str(self.dimensiony)}
                if at != None:
                    mxargs["type"] = at
                                    
                mtx = etree.SubElement(pv, '{http://www.lexical.org.uk/golem}matrix', 
                                       **mxargs)
            # range?
            if hasattr(self, "minimum") or hasattr(self, "maximum"):
                range = etree.SubElement(pv, "{http://www.lexical.org.uk/golem}range")
                if hasattr(self, "minimum") and self.minimum is not None:
                    min = etree.SubElement(range, "{http://www.lexical.org.uk/golem}minimum")
                    min.text = str(self.minimum)
                if hasattr(self, "maximum") and self.maximum is not None:
                    max = etree.SubElement(range, "{http://www.lexical.org.uk/golem}maximum")
                    max.text = str(self.maximum)
                
            # enumeration?
            if hasattr(self, "possibleValues"):
                if len(self.possibleValues) > 0:
                    enum = etree.SubElement(pv, "{http://www.lexical.org.uk/golem}enumeration")
                    for val in self.possibleValues:
                        v = etree.SubElement(enum, "{http://www.lexical.org.uk/golem}value")
                        v.text = str(val)
        # now templates, which are difficult and weird...
        # so you just have to edit them by hand. given templates are deep
        # magic at the best of times, this is probably acceptable
        for role in self.txml:
            entry.append(self.txml[role])
        # and return
        return entry

    def with_predicate(self, predicate):
        """\
Set a predicate (condition) on a particular Entry instance.

This predicate will be honoured on subsequent calls to x.findin for
entry x; it takes the form of an XPath function."""
        c = copy.copy(self)
        c.predicate = predicate
        return c

    def findin_context(self, *trees):
        """ Find instances of this dictionary entry in a (set of) 
        ElementTrees or filenames. Returns a set of nodes pointing into the
        searched ElementTrees."""

        # We return a list of xml.etrees, each of which matches either
        # this dictionary entry or (if necessary) any dictionary entries
        # which implement the one requested.
        
        # First, convert any filenames into ElementTrees...
        newtrees = []
        for x in trees:
            if isinstance(x, basestring):
                newtrees.append(etree.parse(x))
            else:
                newtrees.append(x)
        trees = newtrees
        
        xpaths, results = [], []
        imps = self.getAllImplementations()
        if hasattr(self, "predicate"):
            predicate = self.predicate            
        else:
            predicate = None
        for i in imps:
            if hasattr(i, "gxpath"):
                xpaths.append(i.gxpath)
        for path in xpaths:
            for tree in trees:                
                if predicate != None:
                    p = path.path + predicate
                else:
                    p = path.path
                    frags = [x for x in tree.xpath(p, namespaces=namespaces)]
                    results.extend(frags)
        return results

    def findin(self, *trees):
        """\
Find instances of this dictionary entry in a given ElementTree
or set of ElementTrees. This version supplies *new*, rerooted
ElementTrees, not just the old ElementTrees with a pointer to 
the right context - use findin_context for that."""
        
        res = self.findin_context(*trees)
        results = [EntryInstance(self, x) for x in res]
        return results
    
    def getAllImplementations(self):
        """\
Recursively identify and return all entries which <golem:implement> the
current class (and which are in currently-loaded dictionaries)."""
        imps = set([self])
        last_entries = set(["{"+self.namespace+"}"+self.id])
        # First, find all synonyms (and synonyms of synonyms ...) in dictionary
        while len(last_entries) > 0:
            # Each time through, we add any new synonyms found, and remember
            # which have just been added. Break out once we are not adding
            # any new ones.
            new_entries = set()
            for i in last_entries:
                iEntry = self.parentdictionary[i]
                for j in iEntry.Synonyms:
                    try:
                        jEntry = self.parentdictionary[j]
                    except KeyError:
                        continue # Dangling references are fine
                    if not jEntry in imps:
                        imps.add(jEntry)
                        new_entries.add(j)
            last_entries = new_entries
        # Now, for each synonym, find all the implementations recursively,
        # checking for circular references.
        last_entries = set(["{"+self.namespace+"}"+self.id])
        # First, find all synonyms (and synonyms of synonyms ...) in dictionary
        while len(last_entries) > 0:
            # Each time through, we add any new implementations found, andnp, remember
            # which have just been added. Break out once we are not adding
            # any new ones.
            new_entries = set()
            for i in last_entries:
                iEntry = self.parentdictionary[i]
                for j in iEntry.ImplementedBy:
                    try:
                        jEntry = self.parentdictionary[j]
                    except KeyError:
                        continue # Dangling references are fine
                    if jEntry in imps:
                        print "Circular implementation reference found!"
                    imps.add(jEntry)
                    new_entries.add(j)
            last_entries = new_entries
        return imps

    def getChildren(self):
        """\
Recursively identify and return all entries which are <golem:children>
of the current concept - i.e. only ever appear as childNodes of the
(XML) node, or nodes, with which this dictionary entry is associated. """

        children = []
        if len(self.Children) == 0:
            return children
        else:
            for i in self.Children:
                ent = self.parentdictionary[i]
                children.append(ent)
                children.extend(ent.getChildren())
            return children

    def boundscheck(self, arb, ctype=""):
        """\
Check that a given piece of data is of the type, and lies within the bounds,
defined in this dictionary entry. """

        try:
            if ctype == "": ctype = self.type
        except AttributeError:
            if type_warning:
                print >> sys.stderr, "WARNING: %s is typeless" % self.id
            return True
        try:
            arb = ctype(arb)
        except ValueError:
            print >> sys.stderr, "Type check failed", type(arb), self.type
            return False
        
        
        if ("minimum" in dir(self) 
            and self.minimum is not None and arb < self.minimum):
            raise(ValueError("boundscheck: minimum %s %s " % (self.minimum,
                                                              arb)))
        if ("maximum" in dir(self)
            and self.maximum is not None and arb > self.maximum):
            raise(ValueError("boundscheck: maximum"))
        # introspection...
        if 'possibleValues' in dir(self):
            if len(self.possibleValues)>0:
                if arb not in self.possibleValues :
                    raise(ValueError(
                            "boundscheck: not in self.possibleValues"))
        return True

    def matrix_shapecheck(self, l):
        """\
Check that a given matrix is, or can be coerced, into the shape 
defined in this dictionary entry."""

        try:
            if self.symmetric:
                if len(l) != self.dimensiony:
                    print >> sys.stderr, len(l), \
                        self.dimensiony, len(l)!=self.dimensiony
                    raise(ValueError)
                idx = len(l)-1
                while idx>0:
                    if len(l[idx]) != (len(l)-idx):
                        raise(ValueError("matrix_shapecheck"))
                    idx -= 1
            else:
                if (len(l) != self.dimensiony):
                    raise(ValueError("matrix_shapecheck"))
                for x in l:
                    if len(x) != self.dimensionx:
                        raise(ValueError("matrix_shapecheck"))
            return True
        except AttributeError:
            if type_warning:
                print >> sys.stderr, \
                    "WARNING: %s has undefined dimension" % self.id
            return True

    def matrix_boundscheck(self, l):
        """\
Check that the elements of a given matrix have the type, and lie within
the bounds, defined in the current dictionary entry."""

        for row in l:
            for elem in row:            
                if self.boundscheck(elem, ctype=self.atype) == False:
                    raise(ValueError("matrix_boundscheck"))
        return True

    def matrix_coercelist(self, l):
        """Coerce a matrix into a list, left-to-right, top-to-bottom."""
        result = []
        if self.symmetric:
            assert len(l) == (self.dimensionx*(self.dimensionx+1)/2)
            incr = self.dimensionx
            while incr > 0:
                row = [l.pop(0) for x in range(incr)]
                result.append(row)
                incr -= 1
        else:
            assert len(l) == (self.dimensionx*self.dimensiony)
            for y in range(self.dimensiony):
                row = [l.pop(0) for x in range(self.dimensionx)]
                result.append(row)
        # we don't want to discard provenance; l may well not be a list - 
        # it may be a subclass of list with extra data
        # let's check it's empty, though
        assert l == []
        return l.extend(result)

    def list_to_arbdict(self, l):
        """\
Map a matrix onto a dictionary for subsequent output using XSLT.

The algorithm used is:
i) Check that the matrix is of the correct shape and within bounds.
ii) From left to right row-wise from the upper left, number off the 
    matrix elements p1, p2, p3... pn (for an n-element matrix), and
    store these in a dictionary {"p1": p1, "p2": p2 ...}.
iii) Return the resulting dictionary.
"""
        success = self.matrix_shapecheck(l) and self.matrix_boundscheck(l)
        arbd = {}
        idx = 1
        
        for row in l:
            for elem in row:            
                arbd[("p"+str(idx))] = '"' + str(elem) + '"'
                idx += 1
        if success:
            return arbd

    def dcall(self, template, arb):
        """\
        
Internal method (you'll never call this directly); bounds-check a piece
of data and template it into an associated <golem:template> defined in
the dictionary. These are mapped onto Python methods named after the
name of the <golem:template>.

In other words, this is where entry.to_value calls come from."""

        # transforms for arbitrary objects. they're either a number/string, a list, or
        # an elementtree...
        tr = etree.XSLT(template)
        
        if type(arb) == type(etree.Element("null")):
            return tr(arb)

        if type(arb) == list:
            arbdict = self.list_to_arbdict(arb)
        else:
            res = self.boundscheck(arb)
            if res:
                arbdict = {"p1": '"' + str(arb) + '"'}
            else:
                raise(ValueError("Bounds check failed"))
        return tr(etree.Element("null"), **arbdict)

    def __getattr__(self, name):
        # Since some methods are defined by templates, which are inherited
        # via synonymity, and may be added at any stage, we may need to pick
        # such methods up on the fly. This does this.
        # It also gets called every time hasattr is called, which is less helpful.
#        print "in __getattr__", self.id
        imps = self.getAllImplementations()
#        print imps
        for imp in imps:
            if imp.templates:
                for (r,b, i) in imp.templates:
                    imp.sort_out_binding(r, b, i, imp.templates[(r, b, i)], newself=self)
                break
        if name in self.__dict__:
            return getattr(self, name)
        else:
            raise AttributeError

class EntryInstance(object):
    # We don't inherit from Entry here, because it is primarily
    # entry *instance* methods we want, not class methods. We
    # get those (and the class methods for free) through __getattr__
    # below. We don't inherit from ElementTree because you can't,
    # it's forbidden by design.
    def __init__(self, entry, x):
        # entry is the relevant entry (whose instance methods we want.)
        # x is the argument to the associated ElementTree.
        self.entry = entry
        self.tree = etree.ElementTree(x)

    def __getattr__(self, name):
        try:
            # The first argument to Entry.getvalue, for example, needs to be this object,
            # so we curry the Entry function, making its first arg be this self
            x = self.entry.__getattr__(name)
            def f(*args, **kw):
                x = self.entry.__getattr__(name)
                return x(self, *args, **kw)
            return f
        except AttributeError:
            return etree._ElementTree.__getattribute__(self.tree, name)


def loadDictionary(filename):
    """Load a dictionary from a default location on the filesystem.
    
On Windows, this is C:\cmldictionaries\ and must be changed by 
editing golem.py by hand: on Unix, it defaults to ~/.cmldictionaries/
but can be overridden by setting the environment variable
CMLDICTIONARIES.
"""
    # is there an environment variable set telling us where the
    # default location for dictionaries is?

    # if there isn't, default to ~/.cmldictionaries/
    if os.name=="posix":
        try:
            basedir = os.environ["CMLDICTIONARIES"]
        except KeyError:
            try:
                basedir = os.environ["HOME"] + "/.cmldictionaries/"
            except KeyError:
                sys.stderr.write("Dictionary load failure: POSIX but no home directory\n")
                sys.exit(999)
        
    elif os.name=="nt":
        basedir = "c:\\cmldictionaries\\"
    dfile = basedir + filename
    if type_warning:
        sys.stderr.write("Loading dictionaries from %s\n" % basedir)
        sys.stderr.write("Attempting to load: %s\n" % dfile) 
    return Dictionary(dfile)

def _test():
    """\
Run doctests.
"""
    import doctest
    doctest.testmod()
    
if __name__=="__main__":
    _test()
