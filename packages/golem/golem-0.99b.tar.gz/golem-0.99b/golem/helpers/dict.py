# Part of pyGolem. See LICENSE in the root of your distribution for the license.
# Andrew Walkingshaw <andrew@lexical.org.uk>

from lxml import etree
import golem, sys, random, md5
from xml.sax.saxutils import quoteattr

class ConfigError(Exception):
    pass

class input_dict(dict):
    def read_config(self, filename):
        for line in open(filename, "r"):
            frags = line.split()
            if len(frags) == 4:
                self[frags[0]] = input_obj(*frags)
            if len(frags) == 8:
                idetc = frags[0:4]
                remainder = frags[4:]
                for x in range(len(remainder)):
                    if remainder[x] == "None":
                        remainder[x] = None
                    else:
                        remainder[x] = remainder[x].split(",")
                args = idetc + remainder
                self[args[0]] = input_obj(*args)
                
class input_obj(object):
    def __init__(self, inpd, keyword, format, type, bounds=None, shape=None,
                 name=None, options=None):
        self.written = False
        if name != None:
            self.name = name[0] # because of input_dict/read_config
                                # - specifically the remainder stanza
        else:
            self.name = None
        self.id = inpd
        self.keyword = keyword
        if format == "block":
            self.block = True
            self.symmetric = False
        elif format == "sblock":
            self.block = True
            self.symmetric = True
        elif format == "inline":
            self.block = False
        else:
            raise ConfigError("Invalid input configuration file: block syntax")
        if type is "int" or "float" or "string":
            self.type = type
        else:
            raise ConfigError("Invalid input configuration file: unknown type")
        if bounds != None:
            try:
                if bounds[0] != "None":
                    self.min = float(bounds[0])
                else:
                    self.min = None
                if bounds[1] != "None":
                    self.max = float(bounds[1])
                else:
                    self.max = None
            except TypeError:
                raise ConfigError(
                    "Invalid input configuration file: invalid bounds")
            except IndexError:
                raise ConfigError(
                    "Invalid input configuration file: malformed bounds")
        else:
            self.min = None
            self.max = None
        if shape != None:
            try:
                self.xdim = int(shape[0])
                self.ydim = int(shape[1])
            except IndexError:
                raise ConfigError(
                    "Invalid input configuration file: malformed shape")
            except TypeError:
                raise ConfigError(
                    "Invalid input configuration file: invalid shape")
        else:
            self.xdim = 1
            self.ydim = 1

        if options:
            self.options = options
        else:
            self.options = None

    def toggleWritten(self):
        if self.written == False:
            self.written = True
        elif self.written == True:
            self.written = False
            
    def generate_xml_castep(self):
        # and create the XSLT...
        self.toggleWritten()
        gxsl = """
    <golem:template role="arb_to_input" binding="input" input="external">
      <xsl:stylesheet version='1.0' 
                      xmlns:xsl='http://www.w3.org/1999/XSL/Transform'
                      xmlns:cml='http://www.xml-cml.org/schema'>
        <xsl:strip-space elements="*" />
        <xsl:output method="text" />"""
        # calculate size
        # therefore work out what the necessary variable names are
        size = 1 * self.xdim * self.ydim
        params = ["p" + str(x+1) for x in range(size)]
        for p in params:
            gxsl +="""
        <xsl:param name="%s" />""" % p        
        gxsl+="""
        <xsl:template match="/">"""
        if self.block:
            gxsl+="""
        <xsl:text>%%BLOCK %s </xsl:text>
        """ % self.keyword
            for i in range(self.ydim):
                for j in range(self.xdim):
                    param = params.pop(0)
                    gxsl += "<xsl:value-of select='$%s' /><xsl:text> </xsl:text>" % param
                gxsl += """<xsl:text>
</xsl:text>"""
            gxsl += """<xsl:text>%%ENDBLOCK %s</xsl:text>""" % self.keyword
        else:
            gxsl +="""
          <xsl:text>%s </xsl:text><xsl:value-of select="$%s" />""" % \
                (self.keyword, params[0])          
        # add footer
        gxsl += """        </xsl:template>
      </xsl:stylesheet>
    </golem:template>"""
        return gxsl

    def generate_bounds_and_type(self):
        if hasattr(self, "type"):            
            if self.block:
                # we have a matrix
                if self.symmetric:
                    symm = "true"
                else:
                    symm = "false"
                bounds_str = """<golem:possibleValues type="matrix">
    <golem:matrix dimensionx="%s" dimensiony="%s" type="%s" symmetric="%s"/>
""" % (self.xdim, self.ydim, self.type, symm)
                pass
            else:
                # we have inline
                if self.xdim != self.ydim and self.xdim != 1:
                    raise ConfigError("Malformed matrix; inconsistent with \
                                      block format")
                else:
                    bounds_str = """<golem:possibleValues type="%s">
""" % self.type
            
            # now range
            if self.min or self.max:
                bounds_str += """      <golem:range>
"""
                if self.min:
                    bounds_str += """        <golem:min>%s</golem:min>
""" % self.min
                if self.max:
                    bounds_str += """        <golem:max>%s</golem:max>
""" % self.max
                bounds_str += """      </golem:range>
"""
            elif self.options:
                bounds_str += """      <golem:enumeration>
"""
                for option in self.options:
                    bounds_str += """        <golem:value>%s</golem:value>
""" % option
                bounds_str += """      </golem:enumeration>
"""
            bounds_str += """    </golem:possibleValues>
"""                               
            return bounds_str
    
        else:
            return ""
    
class concept(dict):
    def __init__(self, keys, parentConcept):
        dict.__init__(self, keys)
        self.parentConcept = [parentConcept]
        
    def __eq__(self, other):
        if self is None and other is None:
            return True
        elif self is None or other is None:
            return False
        elif dict.__eq__(self, other):
            return True
        else:
            return False

class cmlconcept(concept):
    def __init__(self, keys, parentConcept):
        concept.__init__(self, keys, parentConcept)
        self.payload = None
        self.relative = None

    def prettyprint(self):
        if self["tag"].startswith("{http://www.xml-cml.org/schema}"):
            tag = self["tag"].split("}")[1]
        else:
            tag = self["tag"]
        pstr = "<%s" % tag
        if self["id"] is not None: 
            pstr += " id=" + quoteattr(self["id"])
        if self["dictRef"] is not None:
            pstr += " dictRef=" + quoteattr(self["dictRef"])
        if self["title"] is not None: 
            pstr += " title="+ quoteattr(self["title"])
        if self["name"] is not None:
            pstr += " name=" + quoteattr(self["name"])
        pstr += ">"
        return pstr

    def xpathfragment(self, id=True, title=True):
        if self["tag"].startswith("{http://www.xml-cml.org/schema}"):
            tag = "cml:"+self["tag"].split("}")[1]
        else:
            tag = self["tag"]
        pstr = "%s" % tag
        if self["dictRef"] is not None:
            ns, suffix = self["dictRef"][1:].split("}")
	    addition = """\
[(substring-after(@dictRef, ':')='%s' and @dictRef[../namespace::*[name()=substring-before(../@dictRef,':')]='%s']) or (@dictRef='%s' and namespace::*[name()='']='%s')]""" % (suffix, ns, suffix, ns)
            pstr += addition
        elif self["name"] is not None:
            ns, suffix = self["name"][1:].split("}")
	    addition = """\
[(substring-after(@name, ':')='%s' and @name[../namespace::*[name()=substring-before(../@name,':')]='%s']) or (@name='%s' and namespace::*[name()='']='%s')]""" % (suffix, ns, suffix, ns)
            pstr += addition
        elif self["id"] is not None and id: 
            pstr += ("[@id=" + quoteattr(self["id"]) + "]")
        elif self["title"] is not None and title: 
            pstr += ("[@title=" + quoteattr(self["title"]) + "]")
        return pstr

    def setPayload(self, payloadtype):
        self.payload = payloadtype

    def setRelative(self):
        self.relative = True

    def isRelative(self):
        return self.relative

    def hasPayload(self):
        if self.payload:
            return True

class conceptset(dict):
    def __init__(self, keys):
        # we can fake up a multidimensional array by 
        # indexing on tuples
        dict.__init__(self, {})
        self.keys = keys

    def addconcept(self, concept):
        try:
            tk = ""
            for k in range(1, len(self.keys)):
                if concept[self.keys[k]] is not None:
                    tk = str(k) + "_" + concept[self.keys[k]]
                    break
            if len(tk) == 0:
                if len(concept.parentConcept) == 1 and concept.parentConcept[0] is not None:
                    tk = "childOf_" + concept.parentConcept[0][self.keys[0]]
                else:
                    if concept["tag"] == "{http://www.xml-cml.org/cml}cml":
                        # root element, get out of here
                        raise KeyError
                    tk = md5.md5(str(random.random())).hexdigest()
            keys = concept[self.keys[0]]+tk
            
            # This is a little bit tricky.
            # The first key is the tagname, always. We want to always
            # match on that. We then want to match on whichever of the other
            # keys is the _first_ one defined: i.e., in the CML case,
            # @dictRef, then @id, then @title.
            #
            # However, if none match, then we have a problem, because
            # this node is not explicitly addressible, so we need to 
            # consider the parents. If there are multiple parentConcepts
            # then we bail and assign a unique random key.
            # and we therefore 
            # assume does not match *any* prior existing concept. We
            # therefore generate a unique, random key for this concept.
            #
            # So we construct a dictionary key - as a string - which fulfils
            # these properties.
            existing_concept = self[keys]

            # and if this string matches, we deem the concepts to match
            if concept.parentConcept[0] not in \
                    existing_concept.parentConcept:
                existing_concept.parentConcept.extend(concept.parentConcept)
        except KeyError:
            # stash the concept
            self[keys] = concept
        return concept

def get_namespaced_attribute(element, attribute_name):
    att_raw = element.get(attribute_name)
    try:
        prefix, suffix = att_raw.split(":")
    except ValueError:
        prefix, suffix = None, att_raw
    except AttributeError:
        return None
    try:
        namespace = element.nsmap[prefix]
    except KeyError:
        namespace = element.nsmap[None]
    nse = "{%s}%s" % (namespace, suffix)
    return nse

def parsecmlelement(element, parent):
    tag = element.tag
    if isinstance(tag, basestring):
        if tag != "{http://www.xml-cml.org/schema}metadata":
            name = None
            id = element.get("id")
            dictRef = get_namespaced_attribute(element, "dictRef")
            title = element.get("title")
        else:
            dictRef = None
            name = get_namespaced_attribute(element, "name")
            id = None
            title = None
        return cmlconcept({"tag": tag, "name": name, "dictRef":dictRef, "id":id,  "title":title}, parent)
    else:
        return None

def parsecmltree(element, conceptset, parent=None):
    for e in element.getchildren():
        elem = parsecmlelement(e, parent)
        if elem is not None:
            concept = conceptset.addconcept(elem)
            parsecmltree(e, conceptset, parent=concept)
    return conceptset


def print_tree(concepttree):
    print "digraph elements {"

    for k in concepts:
        for y in [x.parentConcept for x in concepts[k]]:
            rstr = "{rank = same; " + ";".join([('"%s"' % p.prettyprint()) for p in y if (p is not None and isinstance(p["tag"], basestring))]) + "}"
            print rstr
            for z in y:
                for alpha in concepts[k]:
                    if z is not None and alpha is not None:
                        if isinstance(z["tag"], basestring) \
                                and isinstance(alpha["tag"], basestring):
                            print '"%s"->"%s"' % (
                                z.prettyprint(), alpha.prettyprint())
    
    print "}"

def xpath_concept(c, concepts, id=True, title=True):
    if (c["id"] == None and c["dictRef"]==None and \
        c["title"] == None) and c["tag"] != "{http://www.xml-cml.org/schema}metadata":
        # payload concept!
        return None
    else:
        if isinstance(c["tag"], basestring):
            terminated = False
            xpath = c.xpathfragment(id=id, title=title)
            backtrack = [c]
            while True:
                if len(backtrack)==1 and len(backtrack[0].parentConcept)==1:
                    if backtrack[0].parentConcept[0] is not None and \
                            isinstance(backtrack[0].parentConcept[0]["tag"],
                                       basestring):
                        xpath = backtrack[0].parentConcept[0].xpathfragment(
                                                         id=id, title=title)+\
                            "/"+xpath
                        backtrack = backtrack[0].parentConcept
                    else:
                        terminated = True
                        xpath = "/"+xpath
                        break

                else:
                    pcs = []
                    for conc in backtrack:
                        if conc is not None:
                            pcs.extend(conc.parentConcept)
                    if len(pcs) == 0:
                        # we've hit the root node!
                        terminated = True
                        xpath = "/" + xpath
                        break
                    xpf = []
                    breakflag = False
                    if len(pcs) != 1:
                        c.setRelative()
                    for concept in pcs:
                        if concept is not None:
                            xpf.append(concept.xpathfragment(id=id, title=title))
                        else:
                            breakflag = True

                    if breakflag:
                        break

                    for frag in xpf:
                        if frag != xpf[0]:
                            breakflag = True

                    if breakflag:
                        break
                                        
                    xpath = xpf[0]+"/"+xpath
                    backtrack = pcs

            if not terminated:
                # deal with the id-on-root-node case
                if xpath.startswith("cml:cml/"):
                    # we've hit the root node, ergo actually is terminated.
                    xpath = "/" + xpath
                else:
                    xpath = ".//" + xpath
                    c.setRelative()

            return xpath

def print_xpaths(concepts):
    for k in concepts:
        c = concepts[k]
        if c.hasPayload():
            xpath = xpath_concept(c, concepts)
            if xpath is not None:
                print xpath

def print_dictheader(ns, prefix, title):
    header =\
"""<?xml version="1.0"?>
<dictionary 
  namespace="%s"
  dictionaryPrefix="%s" 
  title="%s"
  xmlns="http://www.xml-cml.org/schema"
  xmlns:h="http://www.w3.org/1999/xhtml/"
  xmlns:cml="http://www.xml-cml.org/schema"
  xmlns:xsd="http://www.w3.org/2001/XMLSchema"
  xmlns:golem="http://www.lexical.org.uk/golem"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <metadataList>
    <metadata name="dc:creator" content="golem-kiln" />
  </metadataList>

  <!-- This dictionary created using pyGolem -->
""" % (ns, prefix, title)
    return header

def print_dictfooter():
    footer =\
"""


   <!-- pyGolem Internals. DO NOT EDIT BEYOND THIS POINT UNLESS YOU
        KNOW WHAT YOU ARE DOING - or things will probably stop working. -->
        
   <!--
     XSLT found in this dictionary is licensed according to the following
     terms:
     
     Copyright (c) 2005-2008 Toby White <tow21@cam.ac.uk>
               (c) 2007-2008 Andrew Walkingshaw <andrew@lexical.org.uk>
               
     Permission is hereby granted, free of charge, to any person obtaining 
     a copy of this software and associated documentation files (the 
     "Software"), to deal in the Software without restriction, including 
     without limitation the rights to use, copy, modify, merge, publish, 
     distribute, sublicense, and/or sell copies of the Software, and to 
     permit persons to whom the Software is furnished to do so, subject to 
     the following conditions:

     The above copyright notice and this permission notice shall be 
      included in all copies or substantial portions of the Software.

     THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS 
     OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF 
     MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. 
     IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY 
     CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, 
     TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE 
     SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
   -->

  <entry id="gwtsystem" term="INTERNAL ENTRY for golem web tool use">
    <definition/>
    <description/>
    <metadataList/>
    <golem:seealso>gwtsystem</golem:seealso>
  </entry>

  <entry id="absolute" term="Absolutely-positioned concept">
    <definition>Concept which only occurs once in a document</definition>
    <description>
      <h:p>Absolutely-positioned concepts occur exactly once in a document,
           and therefore do not need to be located by specifying a given 
           grouping concept (or chain of grouping concepts).
      </h:p>
    </description>
    <metadataList>
      <metadata name="dc:author" content="golem-kiln" />
    </metadataList>
    <golem:seealso>gwtsystem</golem:seealso>
  </entry>

  <entry id="relative" term="Relatively-positioned concept">
    <definition>Concept which may occur many times in a document</definition>
    <description>
      <h:p>Relatively-positioned concepts can occur more than once in a 
           document, and therefore need to be located by specifying a given 
           grouping concept (or chain of grouping concepts).
      </h:p>
    </description>
    <metadataList>
      <metadata name="dc:author" content="golem-kiln" />
    </metadataList>
    <golem:seealso>gwtsystem</golem:seealso>
  </entry>

  <entry id="grouping" term="Grouping concept">
    <definition>Concept acting as a container for other concepts</definition>
    <description>
      <h:p>
      Grouping concepts do not directly contain values; instead, they contain
      other, relatively positioned, concepts, which themselves may or may not
      contain values.
      </h:p>
    </description>          
    <metadataList>
      <metadata name="dc:author" content="golem-kiln" />
    </metadataList>
    <golem:seealso>gwtsystem</golem:seealso>
  </entry>

  <entry id="value" term="Value-bearing concept">
    <definition>Concept with a direct payload of data</definition>
    <description>
      <h:p>
        Value-bearing concepts directly contain observables -
        data with a value we can extract and evaluate.
      </h:p>
    </description>
    <metadataList>
      <metadata name="dc:author" content="golem-kiln" />
    </metadataList>
    <golem:seealso>gwtsystem</golem:seealso>
  </entry>

  <entry id="parameterInInput" term="Input parameter">
    <definition>User-specified input parameters for the simulation.</definition>
    <description>
      <h:p>
      </h:p>
    </description>
    <metadataList>
      <metadata name="dc:author" content="golem-kiln" />
    </metadataList>
    <golem:seealso>gwtsystem</golem:seealso>
  </entry>

  <entry id="convertibleToInput" term="Input parameter">
    <definition>User-specified input parameters with defined transforms to
    code-native input.</definition>
    <description>
      <h:p>
      </h:p>
    </description>
    <metadataList>
      <metadata name="dc:author" content="golem-kiln" />
    </metadataList>
    <golem:seealso>gwtsystem</golem:seealso>
  </entry>
  
  <entry id="inFinalProperties" term="Final property">
    <definition>A concept appearing the final properties of a task.</definition>
    <description>
    </description>
    <metadataList>
      <metadata name="dc:author" content="golem-kiln" />
    </metadataList>
    <golem:seealso>gwtsystem</golem:seealso>
  </entry>

  <entry id="atomArray" term="FoX Atom array parser">
    <annotation />
    <definition />
    <description />
    <metadataList />
    <golem:template role="getvalue" binding="pygolem_serialization">
      <xsl:stylesheet version='1.0' 
		xmlns:xsl='http://www.w3.org/1999/XSL/Transform'
		xmlns:cml='http://www.xml-cml.org/schema'
		xmlns:str="http://exslt.org/strings"
		extension-element-prefixes="str"
		>
      <xsl:output method="text" />
      <xsl:template match="/">
        <xsl:apply-templates />
      </xsl:template>
      <xsl:template match="cml:atomArray">
        <xsl:text>[[</xsl:text>
        <xsl:for-each select="cml:atom">
          <xsl:text>["</xsl:text><xsl:value-of select="@elementType" /><xsl:text>"</xsl:text>
          <xsl:text>,</xsl:text>
          <xsl:value-of select="@xFract" />
          <xsl:text>,</xsl:text>
          <xsl:value-of select="@yFract" />
          <xsl:text>,</xsl:text>
          <xsl:value-of select="@zFract" />
          <xsl:text>,</xsl:text>
          <xsl:choose>
            <xsl:when test="@occupancy">
              <xsl:value-of select="@occupancy" />
            </xsl:when>
            <xsl:otherwise>
              <xsl:text>1</xsl:text>
            </xsl:otherwise>
          </xsl:choose>
          <xsl:text>,</xsl:text>
          <xsl:choose>
	    <xsl:when test="@id">
	      <xsl:text>"</xsl:text><xsl:value-of select="@id" /><xsl:text>"</xsl:text>
	    </xsl:when>
	    <xsl:otherwise>
	      <xsl:text>"Unspecified"</xsl:text>
	    </xsl:otherwise>
          </xsl:choose>
          <xsl:choose>
	    <xsl:when test="position() != last()">
	      <xsl:text>],</xsl:text>
	    </xsl:when>
	    <xsl:otherwise>
	      <xsl:text>]</xsl:text>
	    </xsl:otherwise>
          </xsl:choose>
        </xsl:for-each>
        <xsl:text>], ""]</xsl:text>
      </xsl:template>
      </xsl:stylesheet>
    </golem:template>
    <golem:xpath>.//cml:atomArray</golem:xpath>
  </entry>
  
  <entry id="lattice" term="Set of lattice vectors - generic read">
    <annotation />
    <definition />
    <description />
    <metadataList />
    <golem:template role="getvalue" binding="pygolem_serialization">

      <xsl:stylesheet version='1.0' 
		      xmlns:xsl='http://www.w3.org/1999/XSL/Transform'
		      xmlns:cml='http://www.xml-cml.org/schema'
		      xmlns:str="http://exslt.org/strings"
		      extension-element-prefixes="str"
		      >
	<xsl:output method="text" />

	<xsl:template match="/">
	  <xsl:apply-templates />
	</xsl:template>
	
	<xsl:template match="cml:lattice">
	  <xsl:text>[</xsl:text>
	  <xsl:for-each select="cml:latticeVector">
	    <xsl:text>[</xsl:text> 
	    <xsl:for-each select="str:tokenize(string(.), ' ')" >
	      <xsl:choose>
		<xsl:when test="position() != last()">
		  <xsl:value-of select="." /><xsl:text>,</xsl:text>
		</xsl:when>
		<xsl:otherwise>
		  <xsl:value-of select="." />
		</xsl:otherwise>
	      </xsl:choose>
	    </xsl:for-each>
	    <xsl:choose>
	      <xsl:when test="position() != last()">
		<xsl:text>],</xsl:text>
	      </xsl:when>
	      <xsl:otherwise>
		<xsl:text>]</xsl:text>
	      </xsl:otherwise>
	    </xsl:choose>
	  </xsl:for-each>
	  <xsl:text>]</xsl:text>
	</xsl:template>
      </xsl:stylesheet>
    </golem:template>
    <golem:xpath>.//cml:lattice</golem:xpath>
    <golem:possibleValues type="matrix">
      <golem:matrix dimensionx="3" dimensiony="3" type="float" symmetric="false"/>
      <golem:range>
	<golem:minimum>0</golem:minimum>
      </golem:range>
    </golem:possibleValues>
  </entry>
  
  <entry id="metadata" term="Metadata default call">
    <annotation />
    <definition />
    <description />
    <metadataList />
    <golem:template role="getvalue" binding="pygolem_serialization">
        <xsl:stylesheet version='1.0' 
                xmlns:xsl='http://www.w3.org/1999/XSL/Transform'
		xmlns:cml='http://www.xml-cml.org/schema'
		xmlns:str="http://exslt.org/strings"
		xmlns:func="http://exslt.org/functions"
		xmlns:exsl="http://exslt.org/common"
		xmlns:tohw="http://www.uszla.me.uk/xsl/1.0/functions"
		extension-element-prefixes="func exsl tohw str"
		exclude-result-prefixes="exsl func tohw xsl str">
        <xsl:output method="text" />
        <xsl:template match="/">
          <xsl:apply-templates />
        </xsl:template>    
	<xsl:template match="cml:metadata">
	  <xsl:text>["</xsl:text><xsl:value-of select="@content" /><xsl:text>", "golem:metadata"]</xsl:text>
	</xsl:template>
      </xsl:stylesheet>
    </golem:template>
  </entry>
  
  <entry id="matrix" term="Matrix default call">
    <annotation />
    <definition />
    <description />
    <metadataList />
    <golem:template role="getvalue" binding="pygolem_serialization">
        <xsl:stylesheet version='1.0' 
                xmlns:xsl='http://www.w3.org/1999/XSL/Transform'
		xmlns:cml='http://www.xml-cml.org/schema'
		xmlns:str="http://exslt.org/strings"
		xmlns:func="http://exslt.org/functions"
		xmlns:exsl="http://exslt.org/common"
		xmlns:tohw="http://www.uszla.me.uk/xsl/1.0/functions"
		extension-element-prefixes="func exsl tohw str"
		exclude-result-prefixes="exsl func tohw xsl str">
        <xsl:output method="text" />
  
  <func:function name="tohw:isAListOfDigits">
    <!-- look only for [0-9]+ -->
    <xsl:param name="x_"/>
    <xsl:variable name="x" select="normalize-space($x_)"/>
    <xsl:choose>
      <xsl:when test="string-length($x)=0">
        <func:result select="false()"/>
      </xsl:when>
      <xsl:when test="substring($x, 1, 1)='0' or
                      substring($x, 1, 1)='1' or
                      substring($x, 1, 1)='2' or
                      substring($x, 1, 1)='3' or
                      substring($x, 1, 1)='4' or
                      substring($x, 1, 1)='5' or
                      substring($x, 1, 1)='6' or
                      substring($x, 1, 1)='7' or
                      substring($x, 1, 1)='8' or
                      substring($x, 1, 1)='9'">
        <xsl:choose>
          <xsl:when test="string-length($x)=1">
            <func:result select="true()"/>
          </xsl:when>
          <xsl:otherwise>
            <func:result select="tohw:isAListOfDigits(substring($x, 2))"/>
          </xsl:otherwise>
        </xsl:choose>
      </xsl:when>
      <xsl:otherwise>
        <func:result select="false()"/>
      </xsl:otherwise>
    </xsl:choose>
  </func:function>

  <func:function name="tohw:isAnInteger">
    <!-- numbers fitting [\+-][0-9]+ -->
    <xsl:param name="x_"/>
    <xsl:variable name="x" select="normalize-space($x_)"/>
    <xsl:variable name="try">
      <xsl:choose>
        <xsl:when test="starts-with($x, '+')">
          <xsl:value-of select="substring($x,2)"/>
        </xsl:when>
        <xsl:when test="starts-with($x, '-')">
          <xsl:value-of select="substring($x,2)"/>
        </xsl:when>
        <xsl:otherwise>
          <xsl:value-of select="$x"/>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:variable>
    <func:result select="tohw:isAListOfDigits($try)"/>
  </func:function>

  <func:function name="tohw:isANumberWithoutExponent">
    <!-- numbers fitting [\+-][0-9]+(\.[0-9]*) -->
    <xsl:param name="x"/>
    <xsl:choose>
      <xsl:when test="contains($x, '.')">
        <func:result select="tohw:isAnInteger(substring-before($x, '.')) and
                             tohw:isAListOfDigits(substring-after($x, '.'))"/>
      </xsl:when>
      <xsl:otherwise>
        <func:result select="tohw:isAnInteger($x)"/>
      </xsl:otherwise>
    </xsl:choose>
  </func:function>

  <func:function name="tohw:isAnFPNumber">
    <!-- Try and interpret a string as an exponential number -->
    <!-- should only recognise strings of the form: [\+-][0-9]*\.[0-9]*([DdEe][\+-][0-9]+)? -->
    <xsl:param name="x"/>
    <xsl:choose>
      <xsl:when test="contains($x, 'd')">
        <func:result select="tohw:isANumberWithoutExponent(substring-before($x, 'd')) and
                             tohw:isAnInteger(substring-after($x, 'd'))"/>
      </xsl:when>
      <xsl:when test="contains($x, 'D')">
        <func:result select="tohw:isANumberWithoutExponent(substring-before($x, 'D')) and
                             tohw:isAnInteger(substring-after($x, 'D'))"/>
      </xsl:when>
      <xsl:when test="contains($x, 'e')">
        <func:result select="tohw:isANumberWithoutExponent(substring-before($x, 'e')) and
                             tohw:isAnInteger(substring-after($x, 'e'))"/>
      </xsl:when>
      <xsl:when test="contains($x, 'E')">
        <func:result select="tohw:isANumberWithoutExponent(substring-before($x, 'E')) and
                             tohw:isAnInteger(substring-after($x, 'E'))"/>
      </xsl:when>
      <xsl:otherwise>
         <func:result select="tohw:isANumberWithoutExponent($x)"/>
      </xsl:otherwise>
    </xsl:choose>
  </func:function>
  
      <xsl:output method="text" />
  
      <xsl:template match="/">
        <xsl:apply-templates />
      </xsl:template>
    
      <xsl:template match="cml:matrix">
        <xsl:param name="rowlength">
          <xsl:value-of select="@columns" />
        </xsl:param>
        <xsl:text>[[[</xsl:text>
        <xsl:for-each select="str:tokenize(string(.), ' ')" >
          <xsl:choose>
            <xsl:when test="position() = last()">
              <xsl:choose>
                <xsl:when test="tohw:isAnFPNumber(.)">
                  <xsl:value-of select="." /><xsl:text>]</xsl:text>
                </xsl:when>
                <xsl:otherwise>
                  <xsl:text>"</xsl:text><xsl:value-of select="." /><xsl:text>"]</xsl:text>
                </xsl:otherwise>
              </xsl:choose>
            </xsl:when>
            <xsl:when test="position() mod $rowlength = 0">
              <xsl:choose>
                <xsl:when test="tohw:isAnFPNumber(.)">
                  <xsl:value-of select="." /><xsl:text>],[</xsl:text>
                </xsl:when>
                <xsl:otherwise>
                  <xsl:text>"</xsl:text><xsl:value-of select="." /><xsl:text>"],[</xsl:text>
                </xsl:otherwise>
              </xsl:choose>
            </xsl:when>
            <xsl:otherwise>
              <xsl:choose>
                <xsl:when test="tohw:isAnFPNumber(.)">
                  <xsl:value-of select="." /><xsl:text>,</xsl:text>
                </xsl:when>
                <xsl:otherwise>
                  <xsl:text>"</xsl:text><xsl:value-of select="." /><xsl:text>",</xsl:text>
                </xsl:otherwise>
              </xsl:choose>
            </xsl:otherwise>
          </xsl:choose>
        </xsl:for-each>
        <xsl:text>],</xsl:text>
        <xsl:choose>
          <xsl:when test="@units">
            <xsl:text>"</xsl:text><xsl:value-of select="@units" /><xsl:text>"</xsl:text>
          </xsl:when>
          <xsl:otherwise>
            <xsl:text>""</xsl:text>
          </xsl:otherwise>
        </xsl:choose>
        <xsl:text>]</xsl:text>
      </xsl:template>
      </xsl:stylesheet>
    </golem:template>
    <golem:seealso>gwtsystem</golem:seealso>
  </entry>

  <entry id="cellParameter" term="Cell parameter default call">
    <annotation />
    <definition />
    <description />
    <metadataList />
    <golem:template role="getvalue" binding="pygolem_serialization">
      <xsl:stylesheet version='1.0' 
                      xmlns:xsl='http://www.w3.org/1999/XSL/Transform'
                      xmlns:cml='http://www.xml-cml.org/schema'
                      xmlns:str="http://exslt.org/strings"
                      extension-element-prefixes="str"
                      >
        <xsl:output method="text" />
        
        <xsl:template match="/">
          <xsl:apply-templates />
        </xsl:template>
    
        <xsl:template match="cml:cellParameter[@parameterType='length']">
          <xsl:text>[[[</xsl:text>
          <xsl:for-each select="str:tokenize(string(.), ' ')" >
            <xsl:choose>
              <xsl:when test="position() = last()">
                <xsl:value-of select="." />
              </xsl:when>
              <xsl:otherwise>
                <xsl:value-of select="." /><xsl:text>,</xsl:text>
              </xsl:otherwise>
            </xsl:choose>
          </xsl:for-each>
          <xsl:text>],</xsl:text>
          <xsl:choose>
            <xsl:when test="@units">
              <xsl:text>"</xsl:text><xsl:value-of select="@units" /><xsl:text>"</xsl:text>
            </xsl:when>
            <xsl:otherwise>
              <xsl:text>""</xsl:text>
            </xsl:otherwise>
          </xsl:choose>
          <xsl:text>],[[</xsl:text>
        </xsl:template>
        
        <xsl:template match="cml:cellParameter[@parameterType='angle']">
          <xsl:for-each select="str:tokenize(string(.), ' ')" >
            <xsl:choose>
              <xsl:when test="position() = last()">
                <xsl:value-of select="." />
              </xsl:when>
              <xsl:otherwise>
                <xsl:value-of select="." /><xsl:text>,</xsl:text>
              </xsl:otherwise>
            </xsl:choose>
          </xsl:for-each>
          <xsl:text>],</xsl:text>
          <xsl:choose>
            <xsl:when test="@units">
              <xsl:text>"</xsl:text><xsl:value-of select="@units" /><xsl:text>"</xsl:text>
            </xsl:when>
            <xsl:otherwise>
              <xsl:text>""</xsl:text>
            </xsl:otherwise>
          </xsl:choose>
          <xsl:text>]]</xsl:text>
        </xsl:template>
      </xsl:stylesheet>
    </golem:template>
    <golem:seealso>gwtsystem</golem:seealso>
  </entry>

  <entry id="array" term="Array default call">
    <annotation />
    <definition />
    <description />
    <metadataList />
    <golem:template role="getvalue" binding="pygolem_serialization">
        <xsl:stylesheet version='1.0' 
                xmlns:xsl='http://www.w3.org/1999/XSL/Transform'
		xmlns:cml='http://www.xml-cml.org/schema'
		xmlns:str="http://exslt.org/strings"
		xmlns:func="http://exslt.org/functions"
		xmlns:exsl="http://exslt.org/common"
		xmlns:tohw="http://www.uszla.me.uk/xsl/1.0/functions"
		extension-element-prefixes="func exsl tohw str"
		exclude-result-prefixes="exsl func tohw xsl str">
        <xsl:output method="text" />
    
  <func:function name="golemxsl:escape">
    <xsl:param name="text"/>
    <func:result select='str:replace($text, "&apos;", "\&apos;")'/>
  </func:function>
  
  <func:function name="tohw:isAListOfDigits">
    <!-- look only for [0-9]+ -->
    <xsl:param name="x_"/>
    <xsl:variable name="x" select="normalize-space($x_)"/>
    <xsl:choose>
      <xsl:when test="string-length($x)=0">
        <func:result select="false()"/>
      </xsl:when>
      <xsl:when test="substring($x, 1, 1)='0' or
                      substring($x, 1, 1)='1' or
                      substring($x, 1, 1)='2' or
                      substring($x, 1, 1)='3' or
                      substring($x, 1, 1)='4' or
                      substring($x, 1, 1)='5' or
                      substring($x, 1, 1)='6' or
                      substring($x, 1, 1)='7' or
                      substring($x, 1, 1)='8' or
                      substring($x, 1, 1)='9'">
        <xsl:choose>
          <xsl:when test="string-length($x)=1">
            <func:result select="true()"/>
          </xsl:when>
          <xsl:otherwise>
            <func:result select="tohw:isAListOfDigits(substring($x, 2))"/>
          </xsl:otherwise>
        </xsl:choose>
      </xsl:when>
      <xsl:otherwise>
        <func:result select="false()"/>
      </xsl:otherwise>
    </xsl:choose>
  </func:function>

  <func:function name="tohw:isAnInteger">
    <!-- numbers fitting [\+-][0-9]+ -->
    <xsl:param name="x_"/>
    <xsl:variable name="x" select="normalize-space($x_)"/>
    <xsl:variable name="try">
      <xsl:choose>
        <xsl:when test="starts-with($x, '+')">
          <xsl:value-of select="substring($x,2)"/>
        </xsl:when>
        <xsl:when test="starts-with($x, '-')">
          <xsl:value-of select="substring($x,2)"/>
        </xsl:when>
        <xsl:otherwise>
          <xsl:value-of select="$x"/>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:variable>
    <func:result select="tohw:isAListOfDigits($try)"/>
  </func:function>

  <func:function name="tohw:isANumberWithoutExponent">
    <!-- numbers fitting [\+-][0-9]+(\.[0-9]*) -->
    <xsl:param name="x"/>
    <xsl:choose>
      <xsl:when test="contains($x, '.')">
        <func:result select="tohw:isAnInteger(substring-before($x, '.')) and
                             tohw:isAListOfDigits(substring-after($x, '.'))"/>
      </xsl:when>
      <xsl:otherwise>
        <func:result select="tohw:isAnInteger($x)"/>
      </xsl:otherwise>
    </xsl:choose>
  </func:function>

  <func:function name="tohw:isAnFPNumber">
    <!-- Try and interpret a string as an exponential number -->
    <!-- should only recognise strings of the form: [\+-][0-9]*\.[0-9]*([DdEe][\+-][0-9]+)? -->
    <xsl:param name="x"/>
    <xsl:choose>
      <xsl:when test="contains($x, 'd')">
        <func:result select="tohw:isANumberWithoutExponent(substring-before($x, 'd')) and
                             tohw:isAnInteger(substring-after($x, 'd'))"/>
      </xsl:when>
      <xsl:when test="contains($x, 'D')">
        <func:result select="tohw:isANumberWithoutExponent(substring-before($x, 'D')) and
                             tohw:isAnInteger(substring-after($x, 'D'))"/>
      </xsl:when>
      <xsl:when test="contains($x, 'e')">
        <func:result select="tohw:isANumberWithoutExponent(substring-before($x, 'e')) and
                             tohw:isAnInteger(substring-after($x, 'e'))"/>
      </xsl:when>
      <xsl:when test="contains($x, 'E')">
        <func:result select="tohw:isANumberWithoutExponent(substring-before($x, 'E')) and
                             tohw:isAnInteger(substring-after($x, 'E'))"/>
      </xsl:when>
      <xsl:otherwise>
         <func:result select="tohw:isANumberWithoutExponent($x)"/>
      </xsl:otherwise>
    </xsl:choose>
  </func:function>
  
        <xsl:template match="/">
          <xsl:apply-templates />
        </xsl:template>

        <xsl:template match="cml:array">
          <xsl:variable name="delim">
            <xsl:choose>
               <xsl:when test="@delimiter">
                 <xsl:value-of select="@delimiter" />
               </xsl:when> 
               <xsl:otherwise>
                 <xsl:text> </xsl:text>
               </xsl:otherwise>
            </xsl:choose>
          </xsl:variable>
          <xsl:text>[[</xsl:text>
            <xsl:for-each select="str:tokenize(string(.), $delim)" >
              <xsl:choose>
                <xsl:when test="tohw:isAnFPNumber(.)">
                  <xsl:value-of select="." />
                </xsl:when>
                <xsl:otherwise>
                  <xsl:text>"</xsl:text><xsl:value-of select="." /><xsl:text>"</xsl:text>
                </xsl:otherwise>
              </xsl:choose>
              <xsl:if test="position() != last()">
                <xsl:text>,</xsl:text>
              </xsl:if>
            </xsl:for-each>
          <xsl:text>],</xsl:text>
          <xsl:choose>
            <xsl:when test="@units">
              <xsl:text>"</xsl:text><xsl:value-of select="@units" /><xsl:text>"</xsl:text>
            </xsl:when>
            <xsl:otherwise>
              <xsl:text>""</xsl:text>
            </xsl:otherwise>
          </xsl:choose>
          <xsl:text>]</xsl:text>
        </xsl:template>
      </xsl:stylesheet>
    </golem:template>
    <golem:seealso>gwtsystem</golem:seealso>
  </entry>

  <entry id="scalar" term="Scalar default call">
    <annotation />
    <definition />
    <description />
    <metadataList />
    <golem:template role="getvalue" binding="pygolem_serialization">
        <xsl:stylesheet version='1.0' 
                xmlns:xsl='http://www.w3.org/1999/XSL/Transform'
		xmlns:cml='http://www.xml-cml.org/schema'
		xmlns:str="http://exslt.org/strings"
		xmlns:func="http://exslt.org/functions"
		xmlns:exsl="http://exslt.org/common"
		xmlns:tohw="http://www.uszla.me.uk/xsl/1.0/functions"
		extension-element-prefixes="func exsl tohw str"
		exclude-result-prefixes="exsl func tohw xsl str">
        <xsl:output method="text" />
  
  
  <func:function name="tohw:isAListOfDigits">
    <!-- look only for [0-9]+ -->
    <xsl:param name="x_"/>
    <xsl:variable name="x" select="normalize-space($x_)"/>
    <xsl:choose>
      <xsl:when test="string-length($x)=0">
        <func:result select="false()"/>
      </xsl:when>
      <xsl:when test="substring($x, 1, 1)='0' or
                      substring($x, 1, 1)='1' or
                      substring($x, 1, 1)='2' or
                      substring($x, 1, 1)='3' or
                      substring($x, 1, 1)='4' or
                      substring($x, 1, 1)='5' or
                      substring($x, 1, 1)='6' or
                      substring($x, 1, 1)='7' or
                      substring($x, 1, 1)='8' or
                      substring($x, 1, 1)='9'">
        <xsl:choose>
          <xsl:when test="string-length($x)=1">
            <func:result select="true()"/>
          </xsl:when>
          <xsl:otherwise>
            <func:result select="tohw:isAListOfDigits(substring($x, 2))"/>
          </xsl:otherwise>
        </xsl:choose>
      </xsl:when>
      <xsl:otherwise>
        <func:result select="false()"/>
      </xsl:otherwise>
    </xsl:choose>
  </func:function>

  <func:function name="tohw:isAnInteger">
    <!-- numbers fitting [\+-][0-9]+ -->
    <xsl:param name="x_"/>
    <xsl:variable name="x" select="normalize-space($x_)"/>
    <xsl:variable name="try">
      <xsl:choose>
        <xsl:when test="starts-with($x, '+')">
          <xsl:value-of select="substring($x,2)"/>
        </xsl:when>
        <xsl:when test="starts-with($x, '-')">
          <xsl:value-of select="substring($x,2)"/>
        </xsl:when>
        <xsl:otherwise>
          <xsl:value-of select="$x"/>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:variable>
    <func:result select="tohw:isAListOfDigits($try)"/>
  </func:function>

  <func:function name="tohw:isANumberWithoutExponent">
    <!-- numbers fitting [\+-][0-9]+(\.[0-9]*) -->
    <xsl:param name="x"/>
    <xsl:choose>
      <xsl:when test="contains($x, '.')">
        <func:result select="tohw:isAnInteger(substring-before($x, '.')) and
                             tohw:isAListOfDigits(substring-after($x, '.'))"/>
      </xsl:when>
      <xsl:otherwise>
        <func:result select="tohw:isAnInteger($x)"/>
      </xsl:otherwise>
    </xsl:choose>
  </func:function>

  <func:function name="tohw:isAnFPNumber">
    <!-- Try and interpret a string as an exponential number -->
    <!-- should only recognise strings of the form: [\+-][0-9]*\.[0-9]*([DdEe][\+-][0-9]+)? -->
    <xsl:param name="x"/>
    <xsl:choose>
      <xsl:when test="contains($x, 'd')">
        <func:result select="tohw:isANumberWithoutExponent(substring-before($x, 'd')) and
                             tohw:isAnInteger(substring-after($x, 'd'))"/>
      </xsl:when>
      <xsl:when test="contains($x, 'D')">
        <func:result select="tohw:isANumberWithoutExponent(substring-before($x, 'D')) and
                             tohw:isAnInteger(substring-after($x, 'D'))"/>
      </xsl:when>
      <xsl:when test="contains($x, 'e')">
        <func:result select="tohw:isANumberWithoutExponent(substring-before($x, 'e')) and
                             tohw:isAnInteger(substring-after($x, 'e'))"/>
      </xsl:when>
      <xsl:when test="contains($x, 'E')">
        <func:result select="tohw:isANumberWithoutExponent(substring-before($x, 'E')) and
                             tohw:isAnInteger(substring-after($x, 'E'))"/>
      </xsl:when>
      <xsl:otherwise>
         <func:result select="tohw:isANumberWithoutExponent($x)"/>
      </xsl:otherwise>
    </xsl:choose>
  </func:function>
        
  <xsl:template match="/">
    <xsl:apply-templates />
  </xsl:template>
  
  <xsl:template match="cml:scalar">
    <xsl:variable name="value">
      <xsl:choose>
	<xsl:when test="tohw:isAnFPNumber(.)">
          <xsl:value-of select="." />
	</xsl:when>
	<xsl:otherwise>
          <xsl:text>"</xsl:text><xsl:value-of select="." /><xsl:text>"</xsl:text>
	</xsl:otherwise>
      </xsl:choose>
    </xsl:variable>
    <xsl:variable name="units">
      <xsl:choose>
	<xsl:when test="@units">
	  <xsl:text>"</xsl:text><xsl:value-of select="@units" /><xsl:text>"</xsl:text>
	</xsl:when>
	<xsl:otherwise>
	  <xsl:text>""</xsl:text>
	</xsl:otherwise>
      </xsl:choose>
    </xsl:variable>
    <xsl:text>[</xsl:text><xsl:value-of select="$value"/><xsl:text>,</xsl:text><xsl:value-of select="$units" /><xsl:text>]</xsl:text>
  </xsl:template>
</xsl:stylesheet>
    </golem:template>

    <golem:template role="defaultoutput">
      <xsl:stylesheet version='1.0' 
                      xmlns:xsl='http://www.w3.org/1999/XSL/Transform'
                      xmlns:cml='http://www.xml-cml.org/schema'
                      xmlns:str="http://exslt.org/strings"
                      extension-element-prefixes="str"
                      >
        <xsl:output method="text" />
        <xsl:param name="name" />
        <xsl:param name="value" />
        <xsl:template match="/">
          <xsl:value-of select='$name' /><xsl:value-of select='$value' />
        </xsl:template>
      </xsl:stylesheet>
    </golem:template>
    <golem:seealso>gwtsystem</golem:seealso>
  </entry>
</dictionary>
"""
    return footer

def print_dictionary(ns, prefix, title, concepts, groupings, model=None,
                     inputdict=None, use_id=True, use_title=True):
    entries = print_dictheader(ns, prefix, title)
    for k in concepts:
        c = concepts[k]
        entries += print_entry(ns, prefix, c,
                               concepts, groupings, model=model, inputdict=inputdict,
                               use_id=use_id, use_title=use_title)
    if inputdict:
        for key in inputdict:
            if not inputdict[key].written:
                print >> sys.stderr, "Writing %s" % inputdict[key].id
                thisentry =\
"""
  <entry id=%s term="">
    <annotation />
    <definition />
    <description />
    <metadataList>
      <metadata name="dc:author" content="golem-kiln" />
    </metadataList>
    %s
    %s
  </entry>
""" % (quoteattr(inputdict[key].id), inputdict[key].generate_xml_castep(),
       inputdict[key].generate_bounds_and_type())
                entries += thisentry
    entries += print_dictfooter()
    return entries

def id_for_concept(concept, prefix, use_id=True, use_title=True):
    if concept['dictRef'] == None:
        if concept['name'] == None:
            if use_id:
                if concept['id'] == None:
                    if use_title:
                        if concept['title'] == None:
                            return None
                
                        else:
                            return 'title_' + concept['title']
                    else:
                        return None
                else:
                    return 'id_' + concept['id']
            else:
                if use_title:
                    if concept['title'] == None:
                        return None
                    else:
                        return 'title_' + concept['title']
                else:    
                    return None
        else:            
            return concept['name'].split("}")[1]
    return concept['dictRef'].split("}")[1]

def getParents(concept, prefix, use_id=True, use_title=True):
    res = []
    for c in concept.parentConcept:
        if c is None:
            return res
        else:
            dr = id_for_concept(c, prefix, use_id, use_title)
            if dr is not None:
                res += [dr]
            else:
                res += getParents(c, prefix, use_id, use_title)
    return res
        
#    for cx in concept.parentConcept:
#        if cx is not None:
#            dr = id_for_concept(cx, prefix)
#            print "DR:", dr
#            if dr is not None:
#                res.append(dr)
#            else:
#                res.extend(getParents(cx, prefix))
#        else:
#            print "None found!", concept, cx, concept.parentConcept
#    return res                                

def print_entry(ns, prefix, c, concepts, groupings, model=None, 
                inputdict=None, use_id=True, use_title=True):
    entry_str = ""
    implements_str = ""
    payload_str = ""
    xpath_str = ""

    xpath = xpath_concept(c, concepts, id=use_id, title=use_title)
    if xpath is not None:
        parents_str = ""
        parents = getParents(c, prefix, use_title, use_id)
        for x in set(parents):
            parents_str += """    <golem:childOf>%s</golem:childOf>
""" % x
                
        xpath_str = \
"""    <golem:xpath>%s</golem:xpath>
""" % xpath
        for key in groupings:
            if key in xpath:
                implements_str +=\
"""    <golem:implements>%s</golem:implements>
""" % groupings[key]
        dictRef = id_for_concept(c, prefix, use_id, use_title)
        if dictRef == None: 
            return "" # no dictionary entry for this concept
        inputxsl = ""
        if inputdict:
            print "checking %s" % dictRef
            if dictRef in inputdict:
                print "found %s" % dictRef
                inputxsl = inputdict[dictRef].generate_xml_castep()
                implements_str +=\
"""    <golem:implements>convertibleToInput</golem:implements>
"""
        term = None
        if model:
            try:
                entry = model["{%s}%s" 
                              % (ns, dictRef)]
                term = entry.term
            except KeyError:
                pass
        
        if term is None and c['title'] is not None:
            term = c['title']
        elif term is None:
            term = ""
        
        # xml IDs, which we're using the dictRef as, are strictly 
        # [a-zA-Z0-9-_]
        dictRef = dictRef.replace(" ","_")
        entry_str =\
            """  <entry id=%s term=%s>
""" % (quoteattr(dictRef), quoteattr(term))

        if (c.hasPayload() and isinstance(c.payload, basestring)):
            if c.payload.startswith("{http://www.xml-cml.org/schema}"):
                payload = c.payload.split("}")[1]
            else:
                payload = c.payload
            if payload in ["scalar", "matrix", "array", "cellParameter", "lattice"]:
                payload_str =\
                    """    <golem:template call="%s" role="getvalue" binding="pygolem_serialization" />
""" % payload
                implements_str +=\
                    """    <golem:implements>value</golem:implements>
"""
            else:
                implements_str +=\
                    """    <golem:implements>grouping</golem:implements>
"""
        elif (c["tag"].startswith("{http://www.xml-cml.org/schema}") and
              c["tag"].split("}")[1] in [
                    "scalar", "matrix", "array", "cellParameter", "metadata", "lattice"]):
            payload_str =\
                """    <golem:template call="%s" role="getvalue" binding="pygolem_serialization" />
""" % c["tag"].split("}")[1]
            implements_str +=\
                """    <golem:implements>value</golem:implements>
"""
        else:
            implements_str +=\
                """    <golem:implements>grouping</golem:implements>
"""
        if c.isRelative():
            implements_str +=\
"""    <golem:implements>relative</golem:implements>
"""
        else:
            implements_str +=\
"""    <golem:implements>absolute</golem:implements>
"""
        definition_str="<definition />"
        description_str="<description />"
        
        pv_str = ""        
        if model:
            try:
                entry = model["{%s}%s" 
                              % (ns, dictRef)]
                definition_str =\
"""<definition>%s</definition>""" % entry.definition
                description_str = etree.tostring(entry.description).strip()
                
                if inputdict:
                    # use input config
                    pv_str = inputdict[dictRef].generate_bounds_and_type()
                else:
                    try:
                        # use model dictionary
                        pv_str = etree.tostring(entry.pvxml).strip()
                    except AttributeError:
                        pass
                # prettyprinting
                if description_str[-1] != "\n":
                    description_str += "\n"
            except KeyError:
                pass        
        entry =\
"""
%s    <annotation />
    %s
    %s    
    <metadataList>
      <metadata name="dc:author" content="golem-kiln" />
    </metadataList>
%s%s
%s
%s%s
    %s
  </entry>
""" % (entry_str, definition_str, description_str, 
       xpath_str, payload_str, inputxsl, implements_str, parents_str, pv_str)
        return entry
    else:
        return ""

def findpayloads(concepts):
    for k in concepts:
        c = concepts[k]
        if c["id"] == None and c["dictRef"]==None and \
                c["title"] == None:
            # payload concept!
            for parent in c.parentConcept:
                if parent is not None:
                    parent.setPayload(c["tag"])
        elif c["name"] != None and c["tag"]=="{http://www.xml-cml.org/schema}metadata":
            c.setPayload(c["tag"])

def make(filenames, namespace, prefix, title, groupings, model=None, inputfn=None, use_id=True, use_title=True):
    if model:
        modeldict = golem.Dictionary(model, asModel=True)
    else:
        modeldict = None

    concepts = conceptset(["tag", "name", "dictRef", "id", "title"])
    for filename in filenames:
        xml = etree.parse(filename)
        root = xml.getroot()
        rootconcept = concepts.addconcept(parsecmlelement(root, None))
        parsecmltree(root, concepts, parent=rootconcept)
    findpayloads(concepts)

    if inputfn:
        inpd = input_dict()
        inpd.read_config(inputfn)
    else:
        inpd = None

    return print_dictionary(namespace, prefix, title, concepts,
                            groupings, model=modeldict, inputdict=inpd,
                            use_id=use_id, use_title=use_title)

def ossiatest():
    modeldict_fn = sys.argv[1]
    print make(
        sys.argv[2:], "http://www.esc.cam.ac.uk/ossia", 
        "ossia", "OSSIA dictionary",
        {
            "/cml:cml/cml:parameterList[@dictRef='input']":"parameterInInput",
       "/cml:cml/cml:propertyList[@id='finalProperties']":"inFinalProperties"
            }, 
        model = modeldict_fn
        )

if __name__ == "__main__":
    ossiatest()
