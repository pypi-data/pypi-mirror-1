#!/usr/bin/env python

# Part of pyGolem. See LICENSE in the root of your distribution for the license.
# Andrew Walkingshaw <andrew@lexical.org.uk>

import golem, urllib, simplejson, sys, types, copy, md5, random
from lxml import etree

class dict_mixin(object):
    def __getentry(cls): 
        return cls.__entry
        
    def __setentry(cls, e):
        cls.__entry = e
        
    entry = property(__getentry, __setentry)
        
class UndefinedUnitError(AttributeError):
    pass

class Unit(object):
    def __init__(self, symbol, uri=None, multiplierToSI=None, offsetToSI=None):
        self.uri = uri
        self.symbol = symbol
        self.multiplierToSI = multiplierToSI
        self.offsetToSI = offsetToSI

    def getSIConverter(self):
        if self.multiplierToSI is not None:
            if self.offsetToSI is None:
                offset = 0
            else:
                offset = self.offsetToSI
            def converter(x):
                return x*self.multiplierToSI + offset
            return converter
        else:
            raise(UndefinedUnitError)

class unit_metaclass(type):
    def __new__(cls, name, bases, dct):
        cls = type.__new__(cls, name, bases, dct)

        def __mod_value(obj):
            if obj.warnings and hasattr(obj, "unit"):
                sys.stderr.write(
"WARNING: performing operation on unit-bearing quantity - unit info will be lost\n")

        # fix up numeric types (self-other signature)
        for attr in ["__add__","__sub__","__mul__","__floordiv__","__mod__",
                    "__divmod__","__lshift__","__rshift__",
                    "__and__", "__xor__", "__or__", "__div__",
                    "__truediv__", "__radd__", "__rsub__", "__rmul__",
                    "__rdiv__", "__rtruediv__", "__rfloordiv__",
                    "__rmod__", "__rdivmod__", "__rpow__","__rlshift__",
                    "__rrshift__", "__rand__", "__rxor__", "__ror__",
                    "__iadd__", "__isub__", "__imul__", "__idiv__",
                    "__itruediv__", "__ifloordiv", "__imod__",
                    "__ilshift__", "__irshift__", "__iand__", "__ixor__",
                    "__ior__", "__coerce__"]:

            def override(self, other, meth=""):
                if hasattr(self.klass, meth):
                    __mod_value(self)
                    if hasattr(c, "unit"): del c.unit
                    return getattr(self.klass, meth)(c, other)
                return NotImplemented
            
            __bound = lambda x,y,z=attr: override(x, y, meth=z)
            setattr(cls, attr, __bound)

        # fix up numeric types(powers), signature (self, other, modulo="")
        for attr in ["__pow__", "__ipow__"]:
            def over_pwr(self, other, modulo=None, meth=""):
                if hasattr(self.klass, meth):
                    if self.warnings and hasattr(self, "unit"):
                        __mod_value(self)
                    return getattr(self.klass, meth)(self, other, modulo)
                return NotImplemented
            __bound = lambda x,y,m=None,z=attr: over_pwr(x,y,m,meth=z)
            setattr(cls, attr, __bound)

                
        # fix up numeric types (self-alone signature)
        for attr in ["__neg__", "__pos__", "__abs__", "__invert__",
                    "__complex__", "__int__", "__float__", "__long__",
                    "__oct__", "__hex__", "__index__"]:
            def over_self(self, meth=""):
                if hasattr(self.klass, meth):
                    __mod_value(self)
                    return getattr(self.klass, meth)(self)
                return NotImplemented
            __bound = lambda x, z=attr: over_self(x, meth=z)
            setattr(cls, attr, __bound)

        def __mod_cont(obj):
            if obj.warnings and hasattr(obj, "unit"):
                sys.stderr.write(
"WARNING: modifying contents of unit-bearing container - unit info will be lost\n")
            
        # container types
        def setitem(self, k, v):
            if hasattr(self.klass, "__setitem__"):
                if self.warnings and hasattr(self, "unit"):
                    __mod_cont(self)
                if hasattr(self, "unit"): del self.unit
                return getattr(self.klass, "__setitem__")(self, k, v)
            else:
                return NotImplemented
        setattr(cls, "__setitem__", setitem)
        
        def delitem(self, k):
            if hasattr(self.klass, "__delitem__"):
                if self.warnings and hasattr(self, "unit"):
                    __mod_cont(self)
                if hasattr(self, "unit"): del self.unit
                return getattr(self.klass, "__delitem__")(self, k)
            else:
                return NotImplemented
        setattr(cls, "__delitem__", delitem)
        
        # sequence types
        def delslice(self, i, j):
            if hasattr(self.klass, "__delslice__"):
                if self.warnings and hasattr(self, "unit"):
                    __mod_cont(self)
                if hasattr(self, "unit"): del self.unit
                return getattr(self.klass, "__delslice__")(self, i, j)
            else:
                return NotImplemented
        setattr(cls, "__delslice__", delslice)
        
        def setslice(self, i, j, seq):
            if hasattr(self.klass, "__setslice__"):
                if self.warnings and hasattr(self, "unit"):
                    __mod_cont(self)
                if hasattr(self, "unit"): del self.unit
                return getattr(self.klass, "__setslice__")(self, i, j, seq)
            else:
                return NotImplemented
        setattr(cls, "__setslice__", setslice)

        # signature: (self, arg)
        for attr in ["append", "extend", "remove"]:
            def override(self, arg, meth=""):
                if hasattr(self.klass, meth):
                    if self.warnings and hasattr(self, "unit"):
                        __mod_cont(self)
                    if hasattr(self, "unit"): del self.unit
                    return getattr(self.klass, meth)(self, arg)
                return NotImplemented
            __bound = lambda x, z=attr: override(x, arg, meth=z)
            setattr(cls, attr, __bound)
        
        def reverse(self):
            if hasattr(self.klass, "reverse"):
                if self.warnings and hasattr(self, "unit"):
                    __mod_cont(self)
                if hasattr(self, "unit"): del self.unit
                return getattr(self.klass, "reverse")(self)
            return NotImplemented
        setattr(cls, "reverse", reverse)
    
        def pop(self, arg=-1):
            if hasattr(self.klass, "pop"):
                if self.warnings and hasattr(self, "unit"):
                    __mod_cont(self)
                if hasattr(self, "unit"): del self.unit
                return getattr(self.klass, "pop")(self, arg)
            return NotImplemented
        setattr(cls, "pop", pop)
        
        def sort(self, *args):
            if hasattr(self.klass, "sort"):
                if self.warnings and hasattr(self, "unit"):
                    __mod_cont(self)
                if hasattr(self, "unit"): del self.unit
                return getattr(self.klass, "sort")(self, *args)
            return NotImplemented
        setattr(cls, "sort", sort)
        
        def insert(self, i, x):
            if hasattr(self.klass, "insert"):
                if self.warnings and hasattr(self, "unit"):
                    __mod_cont(self)
                if hasattr(self, "unit"): del self.unit
                return getattr(self.klass, "insert")(self, i, x)
            return NotImplemented
        setattr(cls, "insert", insert)
                    
        return cls
        
class unit_mixin(object):
    # danger! danger!
    __metaclass__ = unit_metaclass
    
    def __getunit(cls): 
        return cls.__unit.symbol
    
    def __geturi(cls):
        return cls.__unit.uri
    
    def __seturi(cls, uri):
        cls.__unit.uri = uri
        
    def __setunit(cls, symbol_or_class): 
        if isinstance(symbol_or_class, Unit):
            cls.__unit = symbol_or_class
        else:
            cls.__unit = Unit(symbol_or_class)

    def __delunit(cls): 
        del cls.__unit

    def __get_as_SI(cls):
        try:
            return cls.__unit.getSIConverter()(self)
        except UndefinedUnitError:
            raise(AttributeError("No SI conversion defined on unit property"))
    
    
    uri = property(__geturi, __seturi)
    unit = property(__getunit, __setunit, __delunit, "'unit' property")
    as_SI = property(__get_as_SI)

def hexstring():
    """ Generate a random hex string based on nothing in particular. """
    return md5.new(str(random.random())).hexdigest()

def golemdata(x, u=None, e=None, warnings=None):
    if warnings == None:
        warnings = golem.data_warning
    klass = type(x)
    class newClass(unit_mixin, dict_mixin, klass):
        def __setproxy(self, klass):
            self.__klass = klass
        def __getproxy(self):
            return self.__klass
        klass = property(__getproxy, __setproxy)
    nc = newClass(x)
    nc.klass = klass
    nc.warnings = warnings
    
    if u is None or u.strip() == "":
        nc.unit = "golem:undefined"        
    elif u.strip() != "":
        nc.unit = u
    if e is not None:
        nc.entry = e
    return nc


class ns_dict_mixin(object):
    class namespaced_dictionary(object):
        def __init__(self, f, namespace):
            self.d = golem.Dictionary(f)
            self.namespace = namespace
        def concept(self, c):
            return self.d["{%s}%s" % (self.namespace, c)]

def json_single(y):
    if isinstance(y, basestring):
        return '"%s"' % y
    else:
        j = simplejson.dumps(y)
        return j
 
def print_rdf_rich(x, resource, property=None):
    """
For a given Golem value x, with units x.unit and concept x.uri,
from URI 'resource', produce an RDF/XML fragment of the form: ::
    
    
    <rdf:Description rdf:about="resource">
      <dictionary:uri rdf:about="resource#fragment">
        <golem:value datatype="http://example.org/json/">JSON literal
        </golem:value>
        <golem:units>unit</golem:units>
      </dictionary:uri>
    </rdf:Description>
    
    """
    
    descnode = etree.Element(
        "{http://www.w3.org/1999/02/22-rdf-syntax-ns#}Description")
    descnode.attrib["{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about"] = \
            resource
             
    if x:
        for y in x:
            if property == None:
                property = x.uri
            valnode = etree.Element(property)
            descnode.append(valnode)
            # we now need to invent a (unique!) URI for each container,
            # which we can do with document fragments...
            fragment_uri = resource + "#" + hexstring()
            # which we can now bind the value and units to.
            payload = etree.Element(
              "{http://www.w3.org/1999/02/22-rdf-syntax-ns#}Description")
            payload.attrib[
              "{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about"] = \
              fragment_uri    
            
            payload_value = etree.Element(
              "golemrdf:value")
            payload_value.attrib[
              "{http://www.w3.org/1999/02/22-rdf-syntax-ns#}datatype"] = \
              "http://example.com/json/" 
            payload_value.text = json_single(y)
            payload.append(payload_value)
            if hasattr(y, "unit"):
                payload_units = etree.Element(
                  "golemrdf:units")
                payload_units.text = y.unit
                payload.append(payload_units)
            valnode.append(payload)
        return etree.tostring(descnode)
    else:
        return ""   
    
def print_rdf(x, datatype_uri=None, about=None):
    if about == None:
        fileuri = "file://" + urllib.quote(x.filename)
    else:
        fileuri = about
    descnode = etree.Element(
        "{http://www.w3.org/1999/02/22-rdf-syntax-ns#}Description")
    descnode.attrib["{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about"] = \
            fileuri
    
    if x:
        for y in x:
            if datatype_uri:
                valnode = etree.Element(datatype_uri)
            else:
                valnode = etree.Element(x.uri)
            valnode.attrib[
              "{http://www.w3.org/1999/02/22-rdf-syntax-ns#}datatype"] = \
              "http://example.com/json" 
            valnode.text = json_single(y)
            descnode.append(valnode)

        return etree.tostring(descnode)
    else:
        return ""
