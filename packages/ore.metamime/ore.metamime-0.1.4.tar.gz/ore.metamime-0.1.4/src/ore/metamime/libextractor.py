"""
a libextractor implementation of file classification and metadata extraction

$Id: libextractor.py 2009 2007-07-25 20:16:00Z hazmat $
"""

import extractor

from zope.interface import implements
from zope import component

from ore.metamime import interfaces

class ExtractorFileClassifier( object ):

    implements( interfaces.IMimeClassifier )
    
    def __init__(self, context ):
        self.context = context
        self.extractor = extractor.Extractor(defaults=False, libraries='libextractor_mime')

    def queryIMimeType( self ):
        mime_type = self.queryMimeType()
        if not mime_type:
            return None
        utility = component.getUtility( interfaces.IMimeUtility )
        return utility.getIMimeTypeByName( mime_type )
    
    def queryMimeType( self ):
        content = self.context.read()
        extracted = self.extractor.extract(  data=content, size=len( content ))
        del content
        if extracted:
            mime = [e[1] for e in extracted if e[0] == 'mimetype']
            return mime[0]
        return None
        
class GenericFileProperties( object ):
    """ i am a generic file content adapter that expose all my fields
    """
    
    implements( interfaces.IMimeTypeProperties )

    def __init__(self, context, **properties ):
        self.context = context
        for k,v in properties.items():
            setattr( self, k, v )

    def __getitem__( self, name ):
        try:
            return getattr( self, name )
        except AttributeError:
            raise KeyError, name
    
    
class ExtractorMetadataExtractor( object ):
    """
    a generic file metadata extractor using libextractor
    """

    implements( interfaces.IMimeMetadataExtractor )

    # IWriteZopeDublinCore Fields
##     ['title',
##      'description',
##      'created',
##      'modified',
##      'effective',
##      'expires',
##      'creators',
##      'subjects',
##      'publisher',
##      'contributors']
    
    # generated with
    # fs = open('extractor-keys-raw.txt').read()
    # '\n        '.join( map( lambda x: "'%s':(None,None),"%x, fs.splitlines()) )
    schema_mapping = {
        'unknown':(None,None),
        'filename':(None,None),
        'mimetype':(None,None),
        'title' : (None, None), #( IWriteZopeDublinCore, None ),
        'author':(None,None),
        'artist':(None,None),
        'description' : (None,None), #( IWriteZopeDublinCore, None ),
        'comment':(None,None),
        'date': ( None, None),
        'publisher':(None,None),#( IWriteZopeDublinCore, None ),
        'language':(None,None),
        'album':(None,None),
        'genre':(None,None),
        'location':(None,None),
        'version':(None,None),
        'organization':(None,None),
        'copyright':(None,None),
        'subject':(None,None),
        'keywords':(None,None),
        'contributor':(None,None), # needs dublin core qualification
        'resource-type':(None,None),
        'format':(None,None),
        'resource-identifier':(None,None),
        'source':(None,None),
        'relation':(None,None),
        'coverage':(None,None),
        'software':(None,None),
        'disclaimer':(None,None),
        'warning':(None,None),
        'translated':(None,None),
        'creation date':(None,None),
        'modification date':(None,None),
        'creator':(None,None),
        'producer':(None,None),
        'page count':(None,None),
        'page orientation':(None,None),
        'paper size':(None,None),
        'used fonts':(None,None),
        'page order':(None,None),
        'created for':(None,None),
        'magnification':(None,None),
        'release':(None,None),
        'group':(None,None),
        'size':(None,None),
        'summary':(None,None),
        'packager':(None,None),
        'vendor':(None,None),
        'license':(None,None),
        'distribution':(None,None),
        'build-host':(None,None),
        'operating system':(None,None),
        'dependency':(None,None),
        'MD4':(None,None),
        'MD5':(None,None),
        'SHA-0':(None,None),
        'SHA-1':(None,None),
        'RipeMD160':(None,None),
        'resolution':(None,None),
        'category':(None,None),
        'book title':(None,None),
        'priority':(None,None),
        'conflicts':(None,None),
        'replaces':(None,None),
        'provides':(None,None),
        'conductor':(None,None),
        'interpreter':(None,None),
        'owner':(None,None),
        'lyrics':(None,None),
        'media type':(None,None),
        'contact':(None,None),
        'binary thumbnail data':(None,None),
        'publication date':(None,None),
        'camera make':(None,None),
        'camera model':(None,None),
        'exposure':(None,None),
        'aperture':(None,None),
        'exposure bias':(None,None),
        'flash':(None,None),
        'flash bias':(None,None),
        'focal length':(None,None),
        'focal length (35mm equivalent)':(None,None),
        'iso speed':(None,None),
        'exposure mode':(None,None),
        'metering mode':(None,None),
        'macro mode':(None,None),
        'image quality':(None,None),
        'white balance':(None,None),
        'orientation':(None,None),
        'template':(None,None),
        'split':(None,None),
        'product version':(None,None),
        'last saved by':(None,None),
        'last printed':(None,None),
        'word count':(None,None),
        'character count':(None,None),
        'total editing time':(None,None),
        'thumbnails':(None,None),
        'security':(None,None),
        'created by software':(None,None),
        'modified by software':(None,None),
        'revision history':(None,None),
        'lower case conversion':(None,None),
        'company':(None,None),
        'generator':(None,None),
        'character set':(None,None),
        'line count':(None,None),
        'paragraph count':(None,None),
        'editing cycles':(None,None),
        'scale':(None,None),
        'manager':(None,None),
        'director':(None,None),
        'duration':(None,None),
        'information':(None,None),
        'full name':(None,None),
        'chapter':(None,None),        
        }
    
    def __init__(self, context ):
        self.context = context
        self.extractor = extractor.Extractor(defaults=True)
        
    def extract( self ):
        content = self.context.read()
        d = dict( [ (str(k),v) for k,v in self.extractor.extract( data=content, size=len( content ) ) ] )

        return GenericFileProperties( self.context, **d)
