# -*- coding: utf8 -*-

import csv
from StringIO import StringIO
import rum.fields as field_types

def to_utf8(s):
    """ to_utf8(s) converts unicode to str encoded as utf-8
    >>> to_utf8(u'ham')
    'ham'
    >>> to_utf8(u'eggs')
    'eggs'
    """
    if not isinstance(s, str):
        s=unicode(s)
        s=s.encode("utf8")
    return s
        
def to_csv(items, fields):
    r"""
       Gives csv representations of ``items``
       >>> fields=[field_types.String(name="spam", label="spam"), field_types.Integer(name="eggs", label="eggs")]
       >>> class HamEggs(object): pass
       >>> o1=HamEggs()
       >>> o2=HamEggs()
       >>> o1.spam="3"
       >>> o1.eggs=3
       >>> o2.spam="seven"
       >>> o2.eggs=9
       >>> items=[o1, o2]
       >>> to_csv(items, fields)
       'spam,eggs\r\n3,3\r\nseven,9\r\n'
    """
    stream=StringIO()
    writer=csv.writer(stream)
    writer.writerow([f.label for f in fields])
    for i in items:
        writer.writerow([to_utf8(getattr(i, f.name)) for f in fields])
    value=stream.getvalue()
    stream.close()
    return value
    
    