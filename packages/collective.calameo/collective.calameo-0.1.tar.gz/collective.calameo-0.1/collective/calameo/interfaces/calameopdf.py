from zope import schema
from zope.interface import Interface

from zope.app.container.constraints import contains
from zope.app.container.constraints import containers

from collective.calameo import calameoMessageFactory as _

class ICalameoPDF(Interface):
    """Calameo publication in Plone"""
    
    # -*- schema definition goes here -*-
    calameoid = schema.TextLine(
        title=_(u"Calameo Id"), 
        required=True,
        description=_(u"Insert the ID of Calameo publication"),
    )

    width = schema.Int(
        title=_(u"Width"), 
        required=False,
        description=_(u"Insert the width of Calameo Flash applet in pixel"),
    )

    height = schema.Int(
        title=_(u"Height"), 
        required=True,
        description=_(u"Insert the height of Calameo Flash applet in pixel"),
    )

