# Part of pyGolem. See LICENSE in the root of your distribution for the license.
# Andrew Walkingshaw <andrew@lexical.org.uk>

"""Golem resultlist class.

Ties a series of results to the file they came from.

>>> x = resultlist(range(10), filename="test.xml")
>>> print x
[0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
>>> print x.filename
test.xml
"""

class resultlist(list):
    def __init__(self, seq, filename=None):
        list.__init__(self, seq)
        self.filename = filename

def _test():
    import doctest
    doctest.testmod()
    
if __name__=="__main__":
    _test()