from zope.interface import Interface
from zope.interface.interface import InterfaceClass
from zope.schema import Text
from zope.configuration.fields import GlobalInterface
from zope.configuration.fields import GlobalObject
from zope.configuration.fields import Path
from zope.configuration.fields import PythonIdentifier
from zope.configuration.fields import Tokens


class ISynthesizedSchema(Interface):
    """ Base interface for directives which synthesize schemas.
    """
    name = PythonIdentifier(
        title=u"Schema name",
        description=u"Name of the synthesized interface.",
        required=True
        )

    module = GlobalObject(
        title=u"Target module",
        description=u"Module into which the synthesized interface "
                    u"will be added.",
        required=True
        )

    bases = Tokens(title=u'Base Interfaces',
                   description=u'Defaults to (Interface,).',
                   required=False,
                   value_type=GlobalInterface(),
                  )

class ICSVSchemaDirective(ISynthesizedSchema):
    """ Synthesize a schema from a CSV file.

    Example:

     <configure xmlns="http://namespaces.zope.org/zope"
                xmlns:userschema="http://namespaces.zope.org/userschema">

      <userschema:csv
        file="schema.csv"
        name="IUserDefinedSchema"
        module="somepackage.somemodule"
        />

     </configure>
    """
    file = Path(
        title=u"CSV File",
        description=u"Path to the CSV file.  "
                    u"If relative, start from configuring package.",
        required=True
        )

def createCSVSchema(file, module, name, bases):
    """ Synthesize a Zope3 schema interface from 'file'.
 
    o Seat the new schema into 'module' under 'name'.
    """
    from userschema.schema import fromCSV
    schema = fromCSV(open(file), name, module.__name__, bases)
    setattr(module, name, schema)

def CSVSchemaDirective(_context, file, module, name, bases=()):
    # Directive handler for <userschema:csv> directive.

    # N.B.:  We have to create *some* kind of interface early;
    #        to use the synthesized interface in other ZCML directives.
    #        we will overwrite it later during 'createHTMLFormSchema' (in the
    #        "execute" phase).
    dummy = InterfaceClass(name=name)
    setattr(module, name, dummy)

    # Faux action, only for conflict resolution.
    _context.action(
        discriminator = (file, module, name,),
        callable = createCSVSchema,
        args = (file, module, name, bases),
        )

class IHTMLFormSchemaDirective(ISynthesizedSchema):
    """ Synthesize a schema from an HTML form.

    Example:

     <configure xmlns="http://namespaces.zope.org/zope"
                xmlns:userschema="http://namespaces.zope.org/userschema">

      <userschema:htmlform
        file="page_with_form.html"
        form="form_name"
        name="IUserDefinedSchema"
        module="somepackage.somemodule"
        encoding="UTF-8"
        />

     </configure>
    """
    file = Path(
        title=u"HTML File",
        description=u"Path to the HTML file.  "
                    u"If relative, start from configuring package.",
        required=True
        )

    form = PythonIdentifier(
        title=u"Form name",
        description=u"Name of the form element.  "
                    u"If blank, use the first form in the page.",
        required=False
        )

    encoding = Text(
        title=u"Encoding",
        description=u"Encoding of the form file.",
        default=u'UTF-8',
        required=False,
        )


def createHTMLFormSchema(file, module, name, form, bases, encoding):
    """ Synthesize a Zope3 schema interface from 'file'.
 
    o Seat the new schema into 'module' under 'name'.
    """
    from userschema.schema import fromHTMLForm
    schema = fromHTMLForm(open(file), name, form, module.__name__,
                          bases, encoding)
    setattr(module, name, schema)

def HTMLFormSchemaDirective(_context, file, module, name,
                            form=None, bases=(), encoding='UTF-8'):
    # Directive handler for <userschema:htmlform> directive.

    # N.B.:  We have to create *some* kind of interface early;
    #        to use the synthesized interface in other ZCML directives.
    #        we will overwrite it later during 'createHTMLFormSchema' (in the
    #        "execute" phase).
    dummy = InterfaceClass(name=name)
    setattr(module, name, dummy)

    # Faux action, only for conflict resolution.
    _context.action(
        discriminator = (file, module, name,),
        callable = createHTMLFormSchema,
        args = (file, module, name, form, bases, encoding),
        )

class IXMLSchemaDirective(ISynthesizedSchema):
    """ Synthesize a schema from an XML document.

    Example:

     <configure xmlns="http://namespaces.zope.org/zope"
                xmlns:userschema="http://namespaces.zope.org/userschema">

      <userschema:xml
        file="schema.xml"
        element_name="some_schema"
        name="IUserDefinedSchema"
        module="somepackage.somemodule"
        />

     </configure>
    """
    file = Path(
        title=u"XML File",
        description=u"Path to the XML file.  "
                    u"If relative, start from configuring package.",
        required=True
        )

    element_name = PythonIdentifier(
        title=u"Element name",
        description=u"Name of the schema element.  "
                    u"If blank, use the first <schema> elemtn in the document.",
        required=False
        )


def createXMLSchema(file, module, name, element_name, bases):
    """ Synthesize a Zope3 schema interface from 'file'.
 
    o Seat the new schema into 'module' under 'name'.
    """
    from userschema.etree import fromXML
    schema = fromXML(open(file).read(), name, element_name, module.__name__,
                     bases)
    setattr(module, name, schema)

def XMLSchemaDirective(_context, file, module, name,
                       element_name=None, bases=()):
    # Directive handler for <userschema:htmlform> directive.

    # N.B.:  We have to create *some* kind of interface early;
    #        to use the synthesized interface in other ZCML directives.
    #        we will overwrite it later during 'createXMLSchema' (in the
    #        "execute" phase).
    dummy = InterfaceClass(name=name)
    setattr(module, name, dummy)

    # Faux action, only for conflict resolution.
    _context.action(
        discriminator = (file, module, name,),
        callable = createXMLSchema,
        args = (file, module, name, element_name, bases),
        )
