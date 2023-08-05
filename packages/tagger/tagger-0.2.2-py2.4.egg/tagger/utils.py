from rdflib import Namespace
from datetime import datetime
from types import GeneratorType
import pdb

class nscollection(object):
    """ collection object """
    
    def bindAll(self, graph):
        for key in self.__dict__.keys():
            attr = getattr(self, key)
            if isinstance(attr, Namespace):
                graph.bind(key, attr)

def utcnow():
    now = datetime.utcnow()
    isod = now.date().isoformat()
    isot = now.time().isoformat()
    return u'%sT%sUTC' %(isod, isot)

def any(i):
    return bool([x for x in i if x])

def all(i):
    return len([x for x in i if x])==len(i)

def set_intersect(set1, set2):
    return set1 & set2

def flatten_generators(i):
    for item in i:
        if isinstance(i, GeneratorType):
            yield flatten_generators(i)
        yield i

def debug(trace=True, pm=False):
    def mkfunc(f):
        def wrap(*args, **kwargs):
            try:
                if trace:
                    pdb.set_trace()
                return f(*args, **kwargs)
            except :
                import sys
                pdb.post_mortem(sys.exc_info()[2])
        return wrap
    return mkfunc

# fail gracefull if zope.interface not present
try:
    from zope.interface import Attribute, Interface
    from zope.interface import implements
except ImportError:
    def nullfx(*args, **kwargs):
        pass

    Attribute=nullfx
    implements=nullfx
    
    class Interface(object):
        """how 'bout a keyword guido?"""
