"Demo script adding a __repr__ method to HTTPConnection objects."

import httplib

h = httplib.HTTPConnection('www.python.org')

print h

from partial import *

class HTTPConnection(partial, httplib.HTTPConnection):
    def __repr__(self):
        return ('httplib.HTTPConnection(%s, %s)' % 
                (repr(self.host), repr(self.port)))

print h
