# Part of pyGolem. See LICENSE in the root of your distribution for the license.
# Andrew Walkingshaw <andrew@lexical.org.uk>

import golem
from lxml import etree
import sys

def permute(l):
    # if we're done, return each member of the working list separately
    if len(l) <= 1: return [[x] for x in l[0]]
    # else recurse rightwards
    return [[x]+y for x in l[0] for y in permute(l[1:])]

def _getxpath(entry):
    try:
        return entry.gxpath.path
    except AttributeError:
        return None

def _fixpath(path):
    if path.startswith("/"):
        return path
    else:
        return "/"+path
    

def _xpathsingle(queryset, predicate):
    res = ""
    xpaths = [_getxpath(entry) for entry in queryset]
    # if this permutation contains something unaddressable, return None
    if None in xpaths: return None
    while len(xpaths) >= 2:
        if xpaths[1].startswith(xpaths[0]): 
            # remove duplicates.
            # this doesn't work in the general case, only the specific
            # case of two absolute paths following each other - but that
            # should be good enough given how the dictionary's constructed
            xpaths.pop(0)
        else:
            # part of the xpath, append to result
            path = xpaths.pop(0)
            res += _fixpath(path)
    # last element of the list
    res += _fixpath(xpaths[0])
    if predicate:
        res += predicate
    return res

def xpath(query, templates=False):    
    perms = permute([concept.getAllImplementations() for concept in query])
    predicate = query.getpredicate()
    
    if templates: 
        xpaths = []
        for p in perms:
            xpath = _xpathsingle(p, predicate)
            if xpath is not None:
                try:
                    template = p[-1].templates[("getvalue", 
                                                "pygolem_serialization")]
                    txml = etree.tostring(template)
                except KeyError:
                    txml = None
                xpaths.append((xpath, txml))
    else:            
        xpaths = filter(lambda x: x!=None,
                    [_xpathsingle(l, predicate) for l in perms])
    return xpaths
    
def __test():
    d = golem.Dictionary(
        "/Users/adw27/Documents/workspace/golem/trunk/bin/ossiaDict.xml")
    e = d["{http://www.esc.cam.ac.uk/ossia}emin:finalModule"]
    f = d["{http://www.esc.cam.ac.uk/ossia}OrderParameterSquared"]
    print [e,f]
    print permute([e.getAllImplementations(),f.getAllImplementations()])
    print xpath(golem.db.conceptlist(*[e,f]), templates=True)

if __name__ == "__main__":
    __test()
        
