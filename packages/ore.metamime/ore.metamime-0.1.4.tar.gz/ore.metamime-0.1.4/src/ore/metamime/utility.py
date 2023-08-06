"""
$Id: utility.py 2009 2007-07-25 20:16:00Z hazmat $

## XXX DEPRECEATED ATM, outside of icon usage, and holding mime_type name -> iface mapping
"""

from zope import component
from zope.interface import implements

from persistent import Persistent
from ore.metamime import getIMimeType


import interfaces

class MimeUtility( Persistent ):

    implements( interfaces.IMimeUtility )

    def __init__( self ):
        self.clear()
        
    def registerMime( self, mime_type, icon, mime_marker, mime_schema, mime_factory ):
        self._mimes[ mime_type ] = ( icon, mime_marker, mime_schema, mime_factory )
        self._marker_mimes[ mime_marker.__name__ ] = mime_type
        self._p_changed = 1
        component.provideAdapter( mime_factory, adapts=(mime_marker,), provides=mime_schema )
 
    def getMimeContent( self, file ):
        iface = getIMimeType( file )
        mime_type = getMimeType( file )
        content = component.getAdapter( iface, file, mime_type )
        return content

    def _clear( self ):
        self._mimes = {}
        self._marker_mimes = {}
        
    def getIconURL( self, file ):
        mime_type = self.getMimeType( file )
        if mime_type is None:
            return '++resource++file.png'
        return self._mimes[ mime_type ][0]

    def getIMimeTypeMarkerFor( self, mimetype ):
        return self._mimes[mimetype][1]

    def getIMimeContent( self, file ):
        mime_type = self.getMimeType( file )
        return self._mimes[mime_type][2]

    def getIMimeContentFor( self, mime_type ):
        return self._mimes.get(mime_type,[])[2]
    
    def getMimeType( self, file ):
        iface = getIMimeType( file )
        return self._marker_mimes[ iface.__name__ ]
  
    def extractAndApply( self, file ):
        extractor = interfaces.IMimeMetadataExtractor( file )
        extractor.extractAndApply()
        
    def classifyMimes( self, file ):
        classifier = interfaces.IMimeClassifier( file )
        classifier.classifyAndApply()
        
GlobalMimeUtility = MimeUtility()
