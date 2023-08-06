from zope import schema
from zope.interface import Interface

from zope.app.container.constraints import contains
from zope.app.container.constraints import containers

from collective.splashdancing import splashdancingMessageFactory as _

# -*- extra stuff goes here -*-

class IHTMLClassIDStripper(Interface):
    # a place to place rules for stripping HTML
    # uses the format: 
    # class|discreet

    enabled = schema.Bool(
        title=_(u"Enable HTML Class ID Stripper"),
        description=_(u"Use this box to enable or disable custom HTML stripping"))

    stripping_rules = schema.Text(
        title=_(u"HTML Stripping rules"),
        description=_(u"Place each rule on a separate line"),
        required=True)

