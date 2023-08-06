# Part of pyGolem. See LICENSE in the root of your distribution for the license.
# Andrew Walkingshaw <andrew@lexical.org.uk>


import sys, os, shutil
import golem
from lxml import etree
import md5

class xmldb(object):
    def __init__(self, path):
        """\
open-or-create xml collection

in the flatfile context, that corresponds to a directory, doesn't it...
- so all we do is store the file in the directory.
        """
        # get filelist
        self.files = [x for x in os.listdir(path) if x.endswith(".xml")]
        self.dir = path

    # External
    def add(self, *filenames):
        """ add files to database - which just means copy to directory."""
        for file in filenames:
            shutil.copy(f, self.dir)
        
    def qfile(self, filename, conceptlist, single=False):
        tree = etree.parse(filename)
        xpath = golem.helpers.xpath.xpath(conceptlist)
        res = []
        for x in xpath:
            res.extend(tree.xpath(x, 
                                  conceptlist[-1].parentdictionary.namespaces))

        # and here's a list of the instances we've found!
        if single:
            # ideally we've only got one of these...
            if len(res) != 1: raise AssertionError(
                    "Insufficiently specific search set - \
multiple instances returned.\n")            
        del(tree)
        return res

    # External
    def query(self, *conceptsets):
        # the last concept in each set is the one which bears the evaluator
        # for the XML fragment we're looking for
        
        evaluators = [x[-1] for x in conceptsets]

        rawres = []
        for fn in self.files:
            f = os.path.join(self.dir, fn)
            rawres.append(golem.db.resultlist([], filename=f))
            for conceptlist in conceptsets:
                rawres[-1].extend(self.qfile(f, conceptlist, single=True))
        # so the layout here is that we get a list back per-file
        # of the results - ie a row in our results table. we need
        # to evaluate this, though...
        results = []
        for rawrow in rawres:
            row = golem.db.resultlist([], filename=rawrow.filename)
            for idx in range(len(rawrow)):
                # find the evaluator we want to use
                ev = evaluators[idx]
                row.append(ev.getvalue(rawrow[idx]))
            results.append(row)
        return results

    def query_cached(self, cache, *conceptsets):
        # the last concept in each set is the one which bears the evaluator
        # for the XML fragment we're looking for
        
        evaluators = [x[-1] for x in conceptsets]

        res = []
        for fn in self.files:
            f = os.path.join(self.dir, fn)
            row = golem.db.resultlist([], filename=f)
            res.append(row)
            md5sum = md5.md5(open(f, "r").read()).hexdigest()

            if f in cache and md5sum in cache[f]: # cache is valid for file
                for idx in range(len(conceptsets)):
                    conceptlist = conceptsets[idx]
                    clkey="".join([c.id for c in conceptlist])
                    ev = evaluators[idx]
                    if clkey in cache[f][md5sum]:
                        row.append(cache[f][md5sum][clkey])
                    else:
                        xv = self.qfile(f, conceptlist, single=True)
                        assert(len(xv)==1)
                        val = ev.getvalue(xv[0])
                        row.append(val)
                        cache[f][md5sum][clkey] = val
            else: # file uncached
                cache[f] = {}
                cache[f][md5sum] = {}
                for idx in range(len(conceptsets)):
                    conceptlist = conceptsets[idx]
                    clkey="".join([c.id for c in conceptlist])
                    ev = evaluators[idx]
                    xv = self.qfile(f, conceptlist, single=True)
                    assert(len(xv) == 1)
                    val = ev.getvalue(xv[0])
                    row.append(val)
                    cache[f][md5sum][clkey] = val
        return res

## FIXME: add tests!

if __name__ == "__main__":
    pass
