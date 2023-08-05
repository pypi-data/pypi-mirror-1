""" Convert schema to / from XML format.

$Id: etree.py,v 1.8 2007-06-25 21:29:16 tseaver Exp $
"""
from datetime import timedelta
try:
    from lxml import etree as ElementTree
except ImportError:
    from elementtree import ElementTree
    _COMMENT_CLASS = object() # can't distinguish them with plain ET
else:
    _COMMENT_CLASS = ElementTree.Comment('').__class__

from zope.component import getUtility
from zope.component import ComponentLookupError
from zope.interface import directlyProvides
from zope.interface import implements
from zope.interface import Interface
from zope.interface.interface import InterfaceClass
from zope.schema import ASCII
from zope.schema import ASCIILine
from zope.schema import Bytes
from zope.schema import BytesLine
from zope.schema import Bool
from zope.schema import Choice
from zope.schema import Date
from zope.schema import Datetime
from zope.schema import Float
from zope.schema import Int
from zope.schema import Password
from zope.schema import Set
from zope.schema import SourceText
from zope.schema import Text
from zope.schema import TextLine
from zope.schema import Timedelta
from zope.schema.interfaces import IChoice
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary
 
def _vocabulary(values):
    terms = [SimpleTerm(v, token=hash(v), title=v) for v in values]
    return SimpleVocabulary(terms)

# Zope 3.3 allows both 'sets.Set' and builtin 'set' as values for its Set
# field, while Zope 3.2 allows only 'sets.Set'.
if isinstance(Set._type, tuple):
    SET_TYPE = Set._type[-1]
else:
    SET_TYPE = Set._type

from userschema.schema import ChoiceSet

class ConversionError(ValueError):
    pass

class INodeToField(Interface):
    """ Interface for utilities which convert etree 'field' nodes to fields.
    """
    def __call__(node):
        """ Return a zope.schema.IField, derived from the data in 'node'.
        """

def fromXML(xml_text,
            name=None,
            element_name=None,
            module_name=None,
            bases=None,
            swallow_exceptions=False
           ):
    node = ElementTree.XML(xml_text)
    return fromNode(
        node, name, element_name, module_name, bases, swallow_exceptions)

def fromNode(
    node, name=None, element_name=None, module_name=None, bases=None,
    swallow_exceptions=False):

    if element_name is None:
        schema = node.find('schema')
        element_name = schema.get('name')
    else:
        for x in node.findall('schema'):
            if x.get('name') == element_name:
                schema = x
                break
        else:
            raise ValueError('Unknown schema name: %s' % element_name)

    if name is None:
        name = element_name

    if module_name is None:
        module_name = 'userschema'

    if bases is None:
        bases = (Interface,)

    attrs = {}

    for field in schema.findall('field'):
        field_name = field.get('name')
        field_type = field.get('type')
        try:
            converter = getUtility(INodeToField, field_type)
        except ComponentLookupError:
            if not swallow_exceptions:
                raise
            else:
                continue
        try:
            obj = converter(field)
        except ConversionError:
            if not swallow_exceptions:
                raise
            else:
                continue
        attrs[field_name] = obj

    return InterfaceClass(name=name,
                          bases=tuple(bases),
                          attrs=attrs,
                          __doc__='Generated from XML',
                          __module__=module_name,
                         )

#
#
#
try:
    from zope.datetime import parseDatetimetz
except ImportError:  # BBB for Zope < 3.3
    from zope.app.datetimeutils import parseDatetimetz

def _bool(value):
    return value.lower() == 'true'

def _date(value):
    dt = parseDatetimetz(value)
    assert dt.hour == 0
    assert dt.minute == 0
    assert dt.second == 0
    return dt.date()

def _timedelta(value):
    """ '<days>:<seconds>:<usec>' -> timedelta(days, seconds, usec)
    """
    return timedelta(*map(int, value.split(':')))

_ELEMENT_CONVERTERS = {
    'title': unicode,
    'description': unicode,
    'required': _bool,
    'readonly': _bool,
    'min_length': int,
    'max_length': int,
    'default': None,
    'min': None,
    'max': None,
}

def makeHandler(field_klass, value_converter):
    def _handler(node):
        name = node.get('name')
        if name is None:
            raise ConversionError('Node is unnamed')
        elements = {}
        options = []
        for child in node.getchildren():
            if child.__class__ is _COMMENT_CLASS:
                continue
            tag = child.tag
            converter = _ELEMENT_CONVERTERS.get(tag)
            if converter is None:
                converter = value_converter
            if tag == 'option':
                options.append(converter(child.text))
                continue
            assert tag not in elements
            elements[tag] = converter(child.text)
        if len(options):
            elements['values'] = options
        # XXX hack for ChoiceSet fields. How to do more elegantly?
        # I guess in the ChoiceSet factory?
        if field_klass is ChoiceSet:
            vocabulary = _vocabulary(elements.pop('values'))
            elements['value_type'] = Choice(vocabulary=vocabulary)
            default = elements.get('default')
            if default is not None:
                elements['default'] = SET_TYPE([default])
        return field_klass(__name__=name, **elements)
    _handler.__name__ = '%sHandler' % field_klass.__name__
    directlyProvides(_handler, INodeToField)
    return _handler

TextHandler = makeHandler(Text, unicode)
TextLineHandler = makeHandler(TextLine, unicode)
PasswordHandler = makeHandler(Password, unicode)
IntHandler = makeHandler(Int, int)
BoolHandler = makeHandler(Bool, _bool)
SourceTextHandler = makeHandler(SourceText, unicode)
BytesHandler = makeHandler(Bytes, str)
ASCIIHandler = makeHandler(ASCII, str)
BytesLineHandler = makeHandler(BytesLine, str)
ASCIILineHandler = makeHandler(ASCIILine, str)
FloatHandler = makeHandler(Float, float)
DatetimeHandler = makeHandler(Datetime, parseDatetimetz)
DateHandler = makeHandler(Date, _date)
TimedeltaHandler = makeHandler(Timedelta, _timedelta)
ChoiceHandler = makeHandler(Choice, unicode)
ChoiceSetHandler = makeHandler(ChoiceSet, unicode)
