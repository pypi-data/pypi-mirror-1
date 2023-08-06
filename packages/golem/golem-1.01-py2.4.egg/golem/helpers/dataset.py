# Part of pyGolem. See LICENSE in the root of your distribution for the license.
# Andrew Walkingshaw <andrew@lexical.org.uk>

import sys, golem, generics, pickle, simplejson

class dataset(generics.ns_dict_mixin):
    """ Generic representation of a collection of CML data with an 
attached Golem query (see ``register``) and, optionally, one
or more functions to be fitted to the result of that query 
(see ``addfunction``).
    
For most practical purposes, you're going to want to use
``caching_dataset``, which inherits from this, instead, with the
``golem.db.fs`` driver (``dbformat`` in the class signature.)"""
    
    def __init__(self, dbfile, dbformat, dictionaryfile,
                 dictionarynamespace):

        self.dblibrary = dbformat # bit ugly having to do this
        self.database = dbformat.xmldb(dbfile)
        self.dictionary = self.namespaced_dictionary(dictionaryfile,
                                                     dictionarynamespace)

    def register(self, xconcepts, yconcepts, xpredicate=None, 
                 ypredicate=None, xreducer=None, 
                 yreducer=None):
        """ Attach a query (consisting of a pair of lists of Golem concepts, 
        each producing one datapoint per file) to this dataset.
        
        A dataset may only have one query (and therefore set of fits)
        attached at once; attaching a new query through ``register`` loses
        any previously attached fits or retrieved queries."""
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
        """ Add a function you wish to fit to the data resulting from a query attached
        to this dataset. """
        self.fit.addfunction(name, function, params)

    def dispatch(self, format, cache=None):
        """ Run any fits or queries attached to this dataset, but do not
        return the results. """
        if self.fit.fitters != {}:
            self.fit.fit(cache=cache)
        else:
            self.fit.getdata(cache=cache)

    def makeplot(self, format, graphfile):
        """ Plot any queries and fitted functions attached to this dataset."""
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
        """ Run all queries and function fitting processes attached to this dataset,
        returning the results."""
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
    """ If you're trying to build a program to interact with a large corpus 
of CML, this is a good place to start. 

Arguments:

* ``cachefile``: file in which cached query results against this dataset are saved
* ``dbfile``: path to where the DB we're querying resides
* ``dbformat``: which DB driver you're using. You can plug in new databases here, but most of the time you'll want ``golem.db.fs``, the directory-full-of-files driver.
* ``dictionaryfile``: which CML/Golem dictionary to use for queries.
* ``dictionarynamespace``: Namespace of the above dictionary.

    """
    def __init__(self, cachefile, dbfile, dbformat, dictionaryfile,
                 dictionarynamespace):
        self.cachefile = cachefile
        super(self, caching_dataset).__init__(dbfile, dbformat, 
                                              dictionaryfile, dictionarynamespace)
        self.loadcache()
        self.savecache()

    def loadcache(self):
        """ Load query cache as a pickle."""
        try:
            f = open(self.cachefile, "r")
            self.cache = pickle.load(f)
            f.close()
        except IOError:
            self.cache = {}

    def savecache(self):
        """ Save query cache."""
        f = open(self.cachefile, "w")
        pickle.dump(self.cache, f)
        f.close()
        

    def go(self, graphfile, output=sys.stdout, format="verbose",
           cache=None):
        """ Run any attached queries or fits against this dataset and return the results.
        
        ``graphfile``, here, is the path for a Pelote plot, if you wish to make one;
        ``output`` is a file-like object to write output to, and ``format`` is the
        format in which to return results."""
        if cache==None:
            cache = self.cache
        res = super(caching_dataset, self).go(graphfile, 
                  output=sys.stdout, format=format, cache=cache)
        self.savecache()
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
