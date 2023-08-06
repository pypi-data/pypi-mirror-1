"""
$Id: zcml.py 2259 2008-11-04 22:17:36Z hazmat $
"""

from zope import interface, component
from zope.interface.interface import InterfaceClass
from zope import schema

import interfaces


class IMimeTypeDirective( interface.Interface ):

    mimetype = schema.Text(
        title=u"Mime Type For File",
        description=u"",
        required=True )

    icon = schema.BytesLine(
        title=u"Resource Icon Name For File",
        description=u"",
        required=False )

    marker = schema.InterfaceField(
        title=u"Marker Mime Interface",
        description=u"If not given one will be constructed",
        required=False,
        )

    interface = schema.InterfaceField(
        title=u"MimeType Properties Interface",
        description=u"Interface specifying properties of a file of the given Mime Type",
        required=False
        )


def mime2ifaceName( mimetype ):
    mimetype = mimetype.replace('-', '_')
    major, minor = mimetype.split('/')
    major, minor = major.lower().capitalize(), minor.lower().capitalize()
    return "I%s%s"%( major, minor )

def registerMimeType( *args ):
    utility = component.getUtility( interfaces.IMimeUtility )
    utility.registerMime( *args )
    
def handler( context, mimetype, icon=None, marker=None, interface=None, adapter=None):

    if icon is None:
        icon = "++resource++file.png"

    if marker is None:
        iface_name = mime2ifaceName( mimetype )
        marker = InterfaceClass( iface_name, (interfaces.IMimeType,) )

    if interface is None:
        interface = interfaces.IMimeTypeProperties

    marker.setTaggedValue("mime_type", mimetype )
    
    context.action(
        discriminator=('MimeType', mimetype),
        callable=utility.registerMimeType,
        args=( mimetype, icon, marker, interface, adapter )
        )
    
    

    
