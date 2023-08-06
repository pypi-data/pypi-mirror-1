"""
Generic implementation of extractors, classifiers that defer to more specific implementations
"""

from zope import interface, component
import interfaces

class MimeMetadataExtractor( object ):
    
    interface.implements( interface.IMimeMetadataExtractor )

    def __init__( self, context ):
        self.context = context
        
    def extract( self ):

        for name, adapter in component.getAdapters( self.context, interfaces.IMimeMetadataExtractor ):
            if not name: # ourselves
                continue
            values = adapter.extract()
            if not values:
                continue
            return values

class MimeClassifier( object ):
    
    interface.implements( interface.IMimeClassifier )
    
    def __init__( self, context ):
        self.context = context

    def queryIMimeType( self ):
        mime_type = self.queryMimeType()
        utility = component.getUtility( interfaces.IMimeUtility )
        return utility.getIMimeTypeByName( mime_type )
    
    def queryMimeType( self ):
        for name, adapter in component.getAdapters( self.context, interfaces.IMimeClassifier ):
            if not name: # ourselves
                continue
            values = adapter.queryMimeType()
            if not values:
                continue
            return values
        

