"""ZTUtils improvements."""
from logging import getLogger
logger = getLogger('dm.zopepatches.ztutils')


# handle tuple and unicode
def complex_marshal(pairs):
    '''Add request marshalling information to a list of name-value pairs.

    Names must be strings.  Values may be strings, unicode,
    booleans, integers, floats, or DateTimes, and they may also be tuples, lists or
    namespaces containing these types.

    The list is edited in place so that each (name, value) pair
    becomes a (name, marshal, value) triple.  The middle value is the
    request marshalling string.  Integer, float, and DateTime values
    will have ":int", ":float", or ":date" as their marshal string.
    Lists will be flattened, and the elements given ":list" in
    addition to their simple marshal string.  Dictionaries will be
    flattened and marshalled using ":record".
    '''
    def simple_marshal(v):
        """pair specifying the request marshal string and the transformed value."""
        if isinstance(v, str):
            return '', v
        if isinstance(v, unicode):
            return ':utf8:ustring', v.encode('utf-8')
        if isinstance(v, bool):
            return ':boolean', v
        if isinstance(v, int):
            return ':int', v
        if isinstance(v, float):
            return ':float', v
        if isinstance(v, DateTime):
            return ':date', v
        return '', v

    def process_sequence(s, name, suffix=''):
        """a sublist describing marshalling for sequence (list or tuple) *s*."""
        # note: we marshal tuples as "list".
        tag = ':list'
        if not s: return [(name, ':tokens' + suffix, '')] # empty sequence marshalled as tokens
        return [(name, mt + tag + suffix, v)
                for mt, v in map(simple_marshal, s)
                ]
      
    i = len(pairs)
    while i > 0:
        i = i - 1
        k, v = pairs[i]
        m = ''
        sublist = None
        if isinstance(v, str):
            pass
        elif hasattr(v, 'items'):
            sublist = []
            for sk, sv in v.items():
                name = '%s.%s' % (k, sk)
                if isinstance(sv, (list, tuple)):
                    sublist.extend(process_sequence(sv, name, ':record'))
                else:
                    sm, sv = simple_marshal(sv)
                    sublist.append((name, '%s:record' % sm,  sv))
        elif isinstance(v, (list, tuple)):
            sublist = process_sequence(v, k)
        else:
            m, v = simple_marshal(v)
        if sublist is None:
            pairs[i] = (k, m, v)
        else:
            pairs[i:i + 1] = sublist
    return pairs

logger.info('ZTUtils.Zope.complex_marshal patch: now handles tuples and unicode')

from ZTUtils import Zope
Zope.complex_marshal = complex_marshal
