from zope.interface import Interface
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
    schema = fromCSV(name, open(file), module.__name__, bases)
    setattr(module, name, schema)

def CSVSchemaDirective(_context, file, module, name, bases=()):
    # Directive handler for <userschema:csv> directive.

    # N.B.:  We have to do the work early, or else we won't be able
    #        to use the synthesized interface in other ZCML directives.
    createCSVSchema(file, module, name, bases)

    # Faux action, only for conflict resolution.
    _context.action(
        discriminator = (file, module, name,),
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
        />

     </configure>
    """
    file = Path(
        title=u"CSV File",
        description=u"Path to the CSV file.  "
                    u"If relative, start from configuring package.",
        required=True
        )

    form = PythonIdentifier(
        title=u"Form name",
        description=u"Name of the form element.  "
                    u"If blank, use the first form in the page.",
        required=False
        )


def createHTMLFormSchema(file, module, name, form, bases):
    """ Synthesize a Zope3 schema interface from 'file'.
 
    o Seat the new schema into 'module' under 'name'.
    """
    from userschema.schema import fromHTMLForm
    schema = fromHTMLForm(open(file), form, name, module.__name__, bases)
    setattr(module, name, schema)

def HTMLFormSchemaDirective(_context, file, module, name, form=None, bases=()):
    # Directive handler for <userschema:htmlform> directive.

    # N.B.:  We have to do the work early, or else we won't be able
    #        to use the synthesized interface in other ZCML directives.
    createHTMLFormSchema(file, module, name, form, bases)

    # Faux action, only for conflict resolution.
    _context.action(
        discriminator = (file, module, name,),
        )
