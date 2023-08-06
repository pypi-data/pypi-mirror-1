from zope.component import getUtility
from plone.registry.interfaces import IRegistry

from plone.registry import field, Record


def divineFieldType(value):
    v = value
    if isinstance(v, bool):
        schemafield = field.Bool()
    elif isinstance(v, int):
        schemafield = field.Int()
    elif isinstance(v, float):
        schemafield = field.Float()
    elif isinstance(v, basestring):
        schemafield = field.Text()
        v = unicode(v)
    elif isinstance(v, (tuple, list)):
        t = None
        
        # Tuples are immutable, but we might want to marshal the values, so
        # cast to a list.
        if isinstance(v, tuple):
            v = list(v)
        
        for i in range(len(v)):
            # Record the first type it finds
            if t is None:
                t = type(v[i])
            
            # If we deviate from that, kick up a fuss
            if type(v[i]) is not t:
                raise ValueError("%s is not of type %s" % (`v[i]`, `t`))
            
            # Marshall the values, throw away the type for now
            v[i] = divineFieldType(v[i])[1]
        
        # Get the field type and set it as the appropriate value.  Assumes 
        # non-empty tuples as otherwise a judgement can't be made.
        schemafield = field.Tuple(value_type=divineFieldType(v[0][0]))[0]
        
        # We define tuples to be the canonical form of sequences
        return tuple(v)
    else:
        raise ValueError("The type %s is not supported by persistent registries." % (v.__class__))
    return schemafield, v


class InitialGlobalsCompatibilityLayer(object):
    
    def getRegistry(self):
        return getUtility(IRegistry)
    
    def __setitem__(self, k, v):
        schemafield = None
        
        if not k in self.getRegistry():
            schemafield, v = divineFieldType(v)
            record = Record(schemafield)
            record.value = v
            self.getRegistry().records[k] = record
        else:
            self.getRegistry()[k] = v
    
    def __getitem__(self, k):
        return self.getRegistry()[k]