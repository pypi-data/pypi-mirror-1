import zope.dottedname.resolve

from zope import schema
from zope.schema.interfaces import ICollection, IText, IASCII

_resolveCache = {}
def resolve(name):
    global _resolveCache
    item = _resolveCache.get(name, None)
    if item is None:
        _resolveCache[name] = item = zope.dottedname.resolve.resolve(name)
    return item

_typeMap = {
    schema.Int:         'int',
    schema.Float:       'float',
    schema.Bool:        'bool',
    schema.Date:        'date',
    schema.Datetime:    'date',
    schema.TextLine:    'string',
    schema.Text:        'string',
    schema.ASCIILine:   'string',
    schema.ASCII:       'string',
    schema.Choice:      'string',
    schema.Bytes:       'string',
    schema.BytesLine:   'string',
    schema.Password:    'string',
    schema.SourceText:  'string',
    schema.Id:          'string',
    schema.DottedName:  'string',
}

def convertType(field):
    type_name = _typeMap.get(field.__class__, None)
    if type_name is not None:
        return type_name
    if ICollection.providedBy(field):
        if IText.providedBy(field.value_type) or IASCII.providedBy(field.value_type):
            return 'lines'
    for klass, type_name in _typeMap.items():
        if isinstance(field, klass):
            return type_name
    return None