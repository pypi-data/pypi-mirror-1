""" userschema.interfaces

$Id: interfaces.py,v 1.1 2006/09/19 19:52:11 tseaver Exp $
"""
from zope.i18nmessageid import MessageFactory
_ = MessageFactory("zope")

from zope.schema import Field
from zope.schema import TextLine
from zope.schema._field import Set
from zope.schema.interfaces import IChoice
from zope.schema.interfaces import ISet

class IChoiceSet(ISet):
    
    value_type = Field(
        title = _("Value Type"),
        description = _(u"Must be an IChoice field whose vocabulary is a "
                        u"simple string list."))

    default = Set(
        value_type=TextLine(),
        title = _("Default"),
        description = _(u"Default values for the choice set."))
