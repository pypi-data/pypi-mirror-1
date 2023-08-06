# Part of pyGolem. See LICENSE in the root of your distribution for the license.
# Andrew Walkingshaw <andrew@lexical.org.uk>

import sys, golem, generics, pickle, simplejson

class dataset(generics.ns_dict_mixin):
    def __init__(self, dbfile, dbformat, dictionaryfile,
                 dictionarynamespace):
        self.dblibrary = dbformat # bit ugly having to do this
        self.database = dbformat.xmldb(dbfile)
        self.dictionary = self.namespaced_dictionary(dictionaryfile,
                                                     dictionarynamespace)

    def register(self, xconcepts, yconcepts, xpredicate=None, 
                 ypredicate=None, xreducer=None, 
                 yreducer=None):
        xclist=golem.db.conceptlist(
            *[self.dictionary.concept(c) for c in xconcepts])
        yclist=golem.db.conceptlist(
            *[self.dictionary.concept(c) for c in yconcepts])
        self.xconcept=xclist[-1]
        self.yconcept=yclist[-1]
        if xpredicate:
            xclist.setpredicate(xpredicate)
        if ypredicate:
            yclist.setpredicate(ypredicate)
        self.fit = golem.helpers.function.Fit(self.database, xclist, yclist,
                                              xreducer=xreducer,
                                              yreducer=yreducer)
        
    def addfunction(self, name, function, params):
        self.fit.addfunction(name, function, params)

    def dispatch(self, format, cache=None):
        if self.fit.fitters != {}:
            self.fit.fit(cache=cache)
        else:
            self.fit.getdata(cache=cache)

    def makeplot(self, format, graphfile):
        plt=golem.helpers.output.pelote(title=
                                        ("%s v %s" % (self.xconcept.term, 
                                                      self.yconcept.term)))
        plt.addpointlist(data=self.fit.data)
        for k in self.fit.fitters:
            plt.addpointlist(data=self.fit.getfndata(k))
	if graphfile != None:
            plt.write(graphfile)
        if format=="django" and graphfile==None:
            fits = []
            for k in self.fit.fitters:
                fits.append((k, self.fit.getresult(k)))
            plt.serialize()
            return plt.root, self.fit.data, fits
        return True

    def go(self, graphfile, output=sys.stdout, format="verbose",
           cache=None):
        self.dispatch(format, cache=cache)
        # need to go back, add format=="csv", format=="cml"
        if format=="verbose":
            output.write("FIT RESULTS:\n")
            output.write("------------\n\n")
            for k in self.fit.fitters:
                output.write("%s " % k)
                for r in self.fit.getresult(k):
                    output.write("%s " % r)
                output.write("\n")

        elif format=="csv":
            # TODO
            pass
        elif format=="cml":
            # TODO
            pass

        if (format=="verbose" or format=="django"):
            return self.makeplot(format, graphfile)
        elif format=="json":
            self.fit.data.sort()
            d = {"data": self.fit.data}
            for name in self.fit.fitters:
                fd = self.fit.getfndata(name)
                dr = [ [self.fit.data[x][0], fd[x]] for x in range(len(d))]
                d[name] = dr
	    return d

class caching_dataset(dataset):
    def __init__(self, cachefile, dbfile, dbformat, dictionaryfile,
                 dictionarynamespace):
        self.cachefile = cachefile
        dataset.__init__(self, dbfile, dbformat, dictionaryfile,
                         dictionarynamespace)
        self.loadcache()
        self.savecache()

    def loadcache(self):
        try:
            f = open(self.cachefile, "r")
            self.cache = pickle.load(f)
            f.close()
        except IOError:
            self.cache = {}

    def savecache(self):
        f = open(self.cachefile, "w")
        pickle.dump(self.cache, f)
        f.close()
        

    def go(self, graphfile, output=sys.stdout, format="verbose",
           cache=None):
        if cache==None:
            cache = self.cache
        res = super(caching_dataset, self).go(graphfile, 
                  output=sys.stdout, format=format, cache=cache)
        self.savecache()
        print "Cache saved."
        return res

def test():
    pvse = dataset(
        "/Users/adw27/Documents/workspace/golem/trunk/bin/ossiaexamples",
        golem.db.fs, 
        "ossiakiln2.xml",
        "http://www.esc.cam.ac.uk/ossia")
    pvse.register(["temperature"], ["Stiffness"])
    pvse.go('martin.pelote.xml')

if __name__ == "__main__":
    test()
