Using the userschema.schema module
==================================

Importing Schema from CSV Files
-------------------------------

We allow users to spell schema definitions via CSV text files, where the
columns are 'Name', 'Type', 'Default'.  E.g.::

  >>> _SCHEMA = '''\
  ... foo,TextLine,Foo
  ... bar,Int,42
  ... spam,Float,3.1415926
  ... baz,Text,"Multi-line text is
  ... possible in CSV."
  ... qux,Choice,two,one,two,three
  ... quux,ChoiceSet,"two,three",one,two,three
  ... frobnatz,Bool,True'''

When we construct a schema from the CSV, we get a Zope3 interface (just
as though we had typed the equivalent Python faux-class syntax):

  >>> from zope.interface.interface import InterfaceClass
  >>> from zope.schema import Bool
  >>> from zope.schema import Choice
  >>> from zope.schema import Float
  >>> from zope.schema import Int
  >>> from zope.schema import Text
  >>> from zope.schema import TextLine
  >>> from userschema.schema import ChoiceSet
  >>> from userschema.schema import fromCSV

We must pass the name of the generated schema to 'fromCSV', along with
the CSV text (or a file-like object):

  >>> a_schema = fromCSV('a_schema', _SCHEMA)
  >>> type(a_schema) is InterfaceClass
  True
  >>> print a_schema.__name__
  a_schema

The '__module__' attribute of the generated interface defaults to
'userschema':

  >>> print a_schema.__module__
  userschema

We can override that by passing 'module_name':

  >>> a_schema = fromCSV('a_schema', _SCHEMA, module_name='somemodule')
  >>> print a_schema.__module__
  somemodule

The attributes of the generated schema correspond to the rows in
the CSV:

  >>> names = list(a_schema.names())
  >>> names.sort()
  >>> print names
  ['bar', 'baz', 'foo', 'frobnatz', 'quux', 'qux', 'spam']

We create the fields we would expect from the types defined in the CSV.
The 'foo' field is a TextLine:

  >>> field = a_schema.getDescriptionFor('foo')
  >>> isinstance(field, TextLine)
  True
  >>> print field.default
  Foo

The 'bar' field is an Int:

  >>> field = a_schema.getDescriptionFor('bar')
  >>> isinstance(field, Int)
  True
  >>> print field.default
  42

The 'spam' field is an Float:

  >>> field = a_schema.getDescriptionFor('spam')
  >>> isinstance(field, Float)
  True
  >>> print field.default
  3.1415926

The 'baz' field is a Text, with multi-line default:

  >>> field = a_schema.getDescriptionFor('baz')
  >>> isinstance(field, Text)
  True
  >>> print field.default
  Multi-line text is
  possible in CSV.


The 'qux' field is a Choice, with the vocabulary defined in the
extra columns:

  >>> field = a_schema.getDescriptionFor('qux')
  >>> isinstance(field, Choice)
  True
  >>> print field.default
  two
  >>> print [str(x.value) for x in field.vocabulary]
  ['one', 'two', 'three']

The 'quux' field is a ChoiceSet, with the vocabulary defined in the
extra columns:

  >>> field = a_schema.getDescriptionFor('quux')
  >>> isinstance(field, ChoiceSet)
  True
  >>> print field.default
  Set([u'two', u'three'])
  >>> print [str(x.value) for x in field.vocabulary]
  ['one', 'two', 'three']

The 'frobnatz' field is a TextLine:

  >>> field = a_schema.getDescriptionFor('frobnatz')
  >>> isinstance(field, Bool)
  True
  >>> print field.default
  True

Parsing Forms to Make Schemas
-----------------------------

One obvious way to collect user requirements for a schema is to build
the form, iterating it in the browser until the user approves it.
If we want the form to be maintainable by the designer, then we also
need to impose very few requirements on how the form is spelled.

Let's try with a really simple form:

  >>> _SIMPLE_FORM = """\
  ... <html>
  ... <body>
  ... <form name="simple">
  ...  <input type="text" name="favorite_color" value="Blue"
  ...         title="Favorite Color" />
  ...  <input type="checkbox" name="likes_coffee" checked="CHECKED" />
  ...  <input type="radio" name="needs_haircut" value="yes" checked="CHECKED" />
  ...  <input type="radio" name="needs_haircut" value="no" />
  ...  <input type="radio" name="needs_haircut" value="maybe" />
  ...  <select name="plays_instrument">
  ...   <option value="">N/A</option>
  ...   <option value="guitar">Guitar</option>
  ...   <option value="bass">Bass</option>
  ...   <option value="drums">Drums</option>
  ...  </select>
  ...  <textarea name="soliloquy" rows="3" cols="65"
  ...  >To be or not to be?  That is the question.</textarea>
  ...  <textarea name="empty_text" rows="3" cols="65"
  ...  ></textarea>
  ... </form>
  ... </body>
  ... </html>
  ... """

We would like to be able to transform that form into a schema, as:

  >>> from userschema.schema import fromHTMLForm
  >>> a_schema = fromHTMLForm(_SIMPLE_FORM)
  >>> type(a_schema) is InterfaceClass
  True

If we don't override it, the __name__ of the generated interface is
derived from the form element's name attribute:

  >>> print a_schema.__name__
  HTMLForm_simple

We can pass the 'schema_name' to override:

  >>> a_schema = fromHTMLForm(_SIMPLE_FORM, schema_name='ISimple')

  >>> print a_schema.__name__
  ISimple

As with the CSV-generated schema, the '__module__' attribute of the
generated interface defaults to 'userschema':

  >>> print a_schema.__module__
  userschema

We can override that by passing 'module_name':

  >>> a_schema = fromHTMLForm(_SIMPLE_FORM, module_name='somemodule')
  >>> print a_schema.__module__
  somemodule

The attributes of the schema correspond to the form widget names:

  >>> names = list(a_schema.names())
  >>> names.sort()
  >>> print names
  ['empty_text', 'favorite_color', 'likes_coffee', 'needs_haircut', 'plays_instrument', 'soliloquy']

Text input widgets become TextLine fields:

  >>> field = a_schema.getDescriptionFor('favorite_color')
  >>> isinstance(field, TextLine)
  True
  >>> print field.title
  Favorite Color
  >>> print field.default
  Blue

Checkbox widgets become Bool fields:

  >>> field = a_schema.getDescriptionFor('likes_coffee')
  >>> isinstance(field, Bool)
  True
  >>> print field.default
  True

Radio button widgets become Choice fields:

  >>> field = a_schema.getDescriptionFor('needs_haircut')
  >>> isinstance(field, Choice)
  True
  >>> print field.default
  yes
  >>> print [str(x.value) for x in field.vocabulary]
  ['yes', 'no', 'maybe']

Non-multiple select widgets become Choice fields, with more metadata about the
choices (both 'token' and 'value'):

  >>> field = a_schema.getDescriptionFor('plays_instrument')
  >>> isinstance(field, Choice)
  True
  >>> print field.default
  None
  >>> print [(str(x.value), str(x.token)) for x in field.vocabulary]
  [('N/A', ''), ('Guitar', 'guitar'), ('Bass', 'bass'), ('Drums', 'drums')]

Textarea widgets become Text fields:

  >>> field = a_schema.getDescriptionFor('soliloquy')
  >>> isinstance(field, Text)
  True
  >>> print field.default
  To be or not to be?  That is the question.

  >>> field = a_schema.getDescriptionFor('empty_text')
  >>> isinstance(field, Text)
  True
  >>> field.default == u''
  True

We can select from more than one form in the HTML by passing the name of
the form:

  >>> _NAMED_FORM = """\
  ... <html>
  ... <body>
  ... <form name="first">
  ...  <input type="text" name="favorite_color" value="Blue" />
  ... </form>
  ... </body>
  ... <form name="second">
  ...  <input type="text" name="favorite_color" value="Red" />
  ... </form>
  ... </html>
  ... """
  >>> named_schema = fromHTMLForm(_NAMED_FORM, form_name="second")
  >>> print named_schema.__name__
  HTMLForm_second
  >>> field = named_schema.getDescriptionFor('favorite_color')
  >>> isinstance(field, TextLine)
  True
  >>> print field.default
  Red

If we pass the name, but no form matches, fromHTMLForm raises a ValueError:

  >>> fromHTMLForm(_NAMED_FORM, form_name="nonesuch")
  Traceback (most recent call last):
  ...
  ValueError: No matching form: nonesuch

A form which contains multiple checkboxe elements with the same name
yields a field of a new type, IChoiceSet::

  >>> from sets import Set as SetType
  >>> from userschema.interfaces import IChoiceSet
  >>> _CHOICE_SET_FORm = """\
  ... <html>
  ... <body>
  ... <form name="choice_set">
  ...  <input type="checkbox" name="likes_band" value="The Beatles" />
  ...  <input type="checkbox" name="likes_band" value="Led Zepplin"
  ...                       checked="CHECKED"/>
  ...  <input type="checkbox" name="likes_band"
  ...                           value="Emerson, Lake, &amp; Palmer" />
  ...  <input type="checkbox" name="likes_band" value="The Band"
  ...                       checked="CHECKED" />
  ... </form>
  ... </html>
  ... """
  >>> choice_set_schema = fromHTMLForm(_CHOICE_SET_FORm, form_name="choice_set")
  >>> field = choice_set_schema.getDescriptionFor('likes_band')
  >>> IChoiceSet.providedBy(field)
  True

The default value of an IChoiceSet field is itself a set, whose elements
are the values which were checked in the sample form:

  >>> isinstance(field.default, SetType)
  True
  >>> len(field.default)
  2
  >>> 'The Beatles' in field.default
  False
  >>> 'Led Zepplin' in field.default
  True
  >>> 'Emerson, Lake &amp; Palmer' in field.default
  False
  >>> 'The Band' in field.default
  True

The IChoiceSet field also has a vocabulary, made up of *all* the values
of the checkboxes which helped define the field:

  >>> vocab = field.vocabulary
  >>> len(vocab)
  4
  >>> 'The Beatles' in vocab
  True
  >>> 'Led Zepplin' in vocab
  True
  >>> 'Emerson, Lake, & Palmer' in vocab
  True
  >>> 'The Band' in vocab
  True

Select widgets with 'multiple' generate ChoiceSet fields.

  >>> _MULTI_SELECT_FORM = """\
  ... <html>
  ... <body>
  ... <form name="multiselect">
  ...  <select multiple="multiple" name="plays_instrument">
  ...   <option value="">N/A</option>
  ...   <option value="guitar" selected="selected">Guitar</option>
  ...   <option value="bass" selected="selected">Bass</option>
  ...   <option value="drums">Drums</option>
  ...  </select>
  ... </form>
  ... </body>
  ... </html>
  ... """
  >>> multiselect_schema = fromHTMLForm(_MULTI_SELECT_FORM)
  >>> names = list(multiselect_schema.names())
  >>> names.sort()
  >>> print names
  ['plays_instrument']
  >>> field = multiselect_schema.getDescriptionFor('plays_instrument')
  >>> isinstance(field, ChoiceSet)
  True
  >>> isinstance(field.default, SetType)
  True
  >>> len(field.default)
  2
  >>> 'guitar' in field.default
  True
  >>> 'bass' in field.default
  True
  >>> 'drums' in field.default
  False
  >>> print [(str(x.value), str(x.token)) for x in field.vocabulary]
  [('N/A', ''), ('Guitar', 'guitar'), ('Bass', 'bass'), ('Drums', 'drums')]

The form can also use  ZPublisher's marshalling aids (':int', ':float')
to signal field type:

  >>> _MARSHLLED_FORM = """\
  ... <html>
  ... <body>
  ... <form name="multiselect">
  ...  <input type="text" name="age:int" value="42" />
  ...  <input type="text" name="rating:float" value="3.5" />
  ... </form>
  ... </body>
  ... </html>
  ... """
  >>> marshalled_schema = fromHTMLForm(_MARSHLLED_FORM)
  >>> names = list(marshalled_schema.names())
  >>> names.sort()
  >>> print names
  ['age', 'rating']
  >>> field = marshalled_schema.getDescriptionFor('age')
  >>> isinstance(field, Int)
  True
  >>> print field.default
  42
  >>> field = marshalled_schema.getDescriptionFor('rating')
  >>> isinstance(field, Float)
  True
  >>> print field.default
  3.5

CVS: $Id: README.txt,v 1.2 2006/10/03 22:09:51 tseaver Exp $
