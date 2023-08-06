"""
$Id: _base.py 2013 2007-07-26 05:44:38Z hazmat $
"""

from zope import component
from zope.interface import providedBy

import interfaces

def getIMimeType( context ):
    """ get the mime type interface provided by context or raise an error.
    """
    # look for one already  asserted by the context
    for iface in providedBy( context ):
        if iface.extends( interfaces.IMimeType ):
            return iface
    # try to classify the file
    for classifier in component.getAdapters( context, interfaces.IMimeClassifier ):
        iface = classifier.queryIMimeType()
        if iface is not None:
            return iface
    raise AttributeError("no mime interface found")

def getMimeType( context ):
    """ get the mime type string of the content.
    """
    imime = getIMimeType( context )
    return imime.getTaggedValue('mime_type')

def getMimeProperties( context ):
    """ get the mime type metadata of the context, context must be marked with its
    appropriate mime type marker interface.
    """
    mime_type = getMimeType( context )
    # see if we can find a specific properties of this particular mime type
    mime = queryAdapter( IMimeTypeProperties, context, mime_type )
    if mime is not None:
        return mime
    # see if we can find a generic shared mime type properties bag
    mime = getAdapter( IMimeTypeProperites, context )
    return mime


    
