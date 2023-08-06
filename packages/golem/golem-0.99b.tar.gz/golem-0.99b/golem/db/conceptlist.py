# Part of pyGolem. See LICENSE in the root of your distribution for the license.
# Andrew Walkingshaw <andrew@lexical.org.uk>

class conceptlist(list):
    def __init__(self, *args):
        list.__init__(self, list(args))
    def setpredicate(self, predicate):
        self.predicate = predicate
    def getpredicate(self):
        try:
            return self.predicate
        except AttributeError:
            return None
