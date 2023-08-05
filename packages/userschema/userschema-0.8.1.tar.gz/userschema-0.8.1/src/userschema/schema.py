""" userschema.schema

$Id: schema.py,v 1.3 2007/01/31 16:58:07 tseaver Exp $
"""
import csv
import sets
from StringIO import StringIO

from zope.interface import Interface
from zope.interface import implements
from zope.interface.interface import InterfaceClass
from zope.schema import Bool
from zope.schema import Choice
from zope.schema import Float
from zope.schema import Int
from zope.schema import Set
from zope.schema import Text
from zope.schema import TextLine
from zope.schema.interfaces import IChoice
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary

from elementtree.HTMLTreeBuilder import parse as parseHTML

from userschema.interfaces import IChoiceSet

class ChoiceSet(Set):
    implements(IChoiceSet)

    def __init__(self, value_type=None, **kw):
        super(Set, self).__init__(**kw)
        # whine if value_type is not a field
        if value_type is not None and not IChoice.providedBy(value_type):
            raise ValueError("'value_type' must be a choice field.")
        self.vocabulary = value_type.vocabulary

def _from_bool(value):
    return str(value).lower() in ('true', 'yes', 'on')

_TYPES = {'Bool': (Bool, _from_bool),
          'Float': (Float, float),
          'Int': (Int, int),
          'Text': (Text, unicode),
          'TextLine': (TextLine, unicode),
         }

def fromCSV(csv_text, name, module_name=None, bases=None, dialect='excel'):
    """ Synthesize a schema from a CSV file.
    """
    if getattr(csv_text, 'splitlines', None) is not None:
        csv_text = csv_text.splitlines()

    if module_name is None:
        module_name = 'userschema'

    if bases is None:
        bases = (Interface,)

    attrs = {}

    for cols in csv.reader(csv_text, dialect):
        field_name, type_name, default = cols[:3]
        rest = cols[3:]
        if type_name == 'Choice':
            attrs[field_name] = Choice(__name__=field_name,
                                       default=unicode(default),
                                       values=rest,
                                      )
        elif type_name == 'ChoiceSet':
            field = Choice(__name__=field_name,
                           values=rest,
                          )
            default = sets.Set(unicode(default).split(','))
            attrs[field_name] = ChoiceSet(value_type=field,
                                          default=default,
                                         )
        else:
            field_type, converter = _TYPES[type_name]
            attrs[field_name] = field_type(__name__=field_name,
                                           default=converter(default),
                                          )

    return InterfaceClass(name=name, 
                          bases=tuple(bases),
                          attrs=attrs,
                          __doc__='Generated from CSV',
                          __module__=module_name,
                         )


_INPUT_TYPES = {'text': TextLine,
                'checkbox': Bool,
                'radio': Choice,
               }

_MARSHALLED_TYPES = {'int': (Int, int),
                     'float': (Float, float),
                    }


def fromHTMLForm(html_text,
                 name=None,
                 form_name=None,
                 module_name=None,
                 bases=None,
                 encoding='UTF-8',
                ):
    """ Synthesize a schema from an HTML form.
    """
    if getattr(html_text, 'read', None) is not None:
        html_text = html_text.read()

    stream = StringIO(html_text)

    if module_name is None:
        module_name = 'userschema'

    if bases is None:
        bases = (Interface,)

    attrs = {}
    radios = {}
    checkboxes = {}

    etree = parseHTML(stream)
    forms = etree.findall('.//form')

    if len(forms) == 0:
        raise ValueError, 'No forms in html_text.'

    if form_name is not None:
        for candidate in forms:
            if candidate.attrib.get('name') == form_name:
                form = candidate
                break
        else:
            raise ValueError, 'No matching form: %s' % form_name
    else:
        form = forms[0]
        form_name = form.attrib.get('name', '')

    if name is None:
        name = 'HTMLForm_%s' % form_name

    for input in form.findall('.//input'):
        field_name = input.attrib['name']
        title = input.attrib.get('title', '').decode(encoding)
        marshaller_name = None
        if ':' in field_name:
            field_name, marshaller_name = field_name.split(':', 1)
        widget_type = input.attrib['type']
        if widget_type == 'text':
            default = unicode(input.attrib['value'])
        elif widget_type == 'checkbox':
            checked = input.attrib.get('checked', '')
            default = checked.lower() in ('checked', 'true')
            info = {'value': unicode(input.attrib.get('value')),
                    'is_default': checked.lower() in ('checked', 'true'),
                    'title': title,
                   }
            checkboxes.setdefault(field_name, []).append(info)
            continue # defer field creation
        elif widget_type == 'radio':
            checked = input.attrib.get('checked', '')
            info = {'value': unicode(input.attrib['value']),
                    'is_default': checked.lower() in ('checked', 'true'),
                    'title': title,
                   }
            radios.setdefault(field_name, []).append(info)
            continue # defer field creation
        if marshaller_name is not None:
            field_type, converter = _MARSHALLED_TYPES[marshaller_name]
            default = converter(default)
        else:
            field_type = _INPUT_TYPES[widget_type]
        attrs[field_name] = field_type(__name__=field_name,
                                       title=title,
                                       default=default,
                                      )

    for field_name, infos in radios.items():
        default = None
        values = []
        for info in infos:
            values.append(info['value'])
            if info['is_default']:
                default = info['value']
        attrs[field_name] = Choice(__name__=field_name,
                                   values=values,
                                   default=default,
                                   title=info['title'],
                                  )

    for field_name, infos in checkboxes.items():
        if len(infos) == 1:
            attrs[field_name] = Bool(__name__=field_name,
                                     default=infos[0]['is_default'],
                                     title=info['title'],
                                    )
            continue
        default = []
        values = []
        for info in infos:
            values.append(info['value'])
            if info['is_default']:
                default.append(info['value'])
        default = sets.Set(default)
        field = Choice(__name__=field_name,
                       values=values,
                      )
        attrs[field_name] = ChoiceSet(value_type=field,
                                      default=default,
                                      title=info['title'],
                                     )

    for select in form.findall('.//select'):
        field_name = select.attrib['name']
        title = select.attrib.get('title', '').decode(encoding)
        multiple = select.attrib.get('multiple') is not None
        options = []
        for option in select.findall('.//option'):
            selected = option.attrib.get('selected', '')
            value = option.text
            token = option.attrib.get('value', value)
            info = {'token': unicode(token),
                    'value': unicode(value),
                    'is_default': selected.lower() in ('selected', 'true'),
                   }
            options.append(info)

        terms = []
        if multiple:
            default = []
        else:
            default = None
        for info in options:
            terms.append(SimpleTerm(info['value'], info['token']))
            if info['is_default']:
                if multiple:
                    default.append(info['token'])
                else:
                    default = info['value']
        vocabulary = SimpleVocabulary(terms)
        field_type = multiple and ChoiceSet or Choice
        if multiple:
            default = sets.Set(default)
            field = Choice(__name__=field_name,
                           vocabulary=vocabulary)
            attrs[field_name] = ChoiceSet(value_type=field,
                                          default=default,
                                          title=title,
                                         )
        else:
            attrs[field_name] = Choice(__name__=field_name,
                                       vocabulary=vocabulary,
                                       default=default,
                                       title=title,
                                      )

    for textarea in form.findall('.//textarea'):
        field_name = textarea.attrib['name']
        title = textarea.attrib.get('title', '').decode(encoding)
        default = textarea.text
        if default is None:
            default = u''
        else:
            default = default.decode(encoding)
        attrs[field_name] = Text(__name__=field_name,
                                 default=default,
                                 title=title,
                                )

    return InterfaceClass(name=name, 
                          bases=tuple(bases),
                          attrs=attrs,
                          __doc__='Generated from HTML Form',
                          __module__=module_name,
                         )
