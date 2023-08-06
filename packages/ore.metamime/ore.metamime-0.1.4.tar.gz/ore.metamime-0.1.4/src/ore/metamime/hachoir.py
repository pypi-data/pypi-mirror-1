"""
$Id: hachoir.py 2300 2009-03-03 12:59:55Z hazmat $
"""

import tempfile
import hachoir_parser, hachoir_metadata
#from hachoir_parser.guess import createParser
#from hachoir_metadata.metadata import extractMetadata
from hachoir_core.error import HachoirError
from hachoir_core.stream import InputStreamError, InputIOStream

from cStringIO import StringIO
from zope.interface import implements
from zope import component

from ore.metamime import interfaces


def filter_parsers( parser_factory ):
    if 'file_system' in  parser_factory.__module__:
        return True
    return False

class HachoirFileClassifier( object ):

    implements( interfaces.IMimeClassifier )
    
    def __init__( self, context ):
        self.context = context
    
    def queryIMimeType( self ):
        mime_type = self.queryMimeType()
        utility = component.getUtility( interfaces.IMimeUtility )
        return utility.getIMimeTypeByName( mime_type )

    def queryMimeType( self ):
        query_parser = hachoir_parser.QueryParser( [] )
        try:
            stream = self._stream( )
            parser = query_parser.parse( stream )
        except InputStreamError:
            import traceback, sys, pdb
            traceback.print_exc()            
            pdb.post_mortem( sys.exc_info()[-1] )
            raise
        return parser.mime_type

    def _stream( self ):
        return InputIOStream( self.context )
    
class HachoirMetadataExtractor( object ):

    def __init__( self, context ):
        self.context = context

    def extract( self ):
        query_parser = hachoir_parser.QueryParser( [] )
        d = {}        
        try:
            stream = InputIOStream( self.context )
            parser = query_parser.parse( stream )
            metadata = hachoir_metadata.extractMetadata( parser )
            if metadata is None:
                return d
            for item in metadata:
                if not item.values:
                    continue
                d[ item.key ] = item.values[0].value # not bothering with coalescing values for now
            return d
        except InputStreamError:
            import traceback, sys, pdb
            traceback.print_exc()            
            pdb.post_mortem( sys.exc_info()[-1] )
            raise
        return d
