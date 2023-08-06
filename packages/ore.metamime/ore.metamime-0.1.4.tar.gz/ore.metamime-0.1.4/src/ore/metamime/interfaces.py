"""
$Id: interfaces.py 2007 2007-07-25 06:20:35Z hazmat $

"""

from zope.interface import Interface
from zope import schema 

class IMimeTypeProperties( Interface ):
    """
    instance specific mime-type attributes that are common to this mime.
    """

class IMimeType( Interface ):
    """
    a content mime-type, the interface is based off the information with the freedesktop
    shared-mime-project and the associated desktop entry spec.

    IMimeType Interfaces are marker interfaces for context, they can be applied at will.
    """

    def __getitem__( self, name ):
        """
        return metadata with the given name, not all mimetype metadata keys are easily
        might be useuable attributes, so we expose a mapping interface to get them else.
        """

class IMimeClassifier( Interface ):
    """
    classify a file according to its introspected mime types, classifiers always inspect
    the file's contents.
    """

    def queryIMimeType( ):
        """
        return the best guess interface of the content.
        """

    def queryMimeType( ):
        """
        return the mime type of the content.
        """
    
class IMimeMetadataExtractor( Interface ):
    """ a mime type metadata extractor """

    def extract( ):
        """
        return a transient mime type properties object corresponding to the extracted metadata
        from context.

        caller is responsible for persisting values.
        """

class IMimeUtility( Interface ):

    def getIconURL( file ):
        """
        return the icon url for a file, based on its mime type
        """

    def queryIMimeType( file ):
        """
        return the best guess interface of the content.
        """

    def queryMimeType( file ):
        """
        return the mime type of the content.
        """

    def getIMimeTypeByName( mime_type ):
        """
        return the mime type interface for the given mime type string.
        """ 


class IMediaContent( IMimeTypeProperties ):
    """ media content marker
    """ 

d = {}
d['required'] = False

class IAudioContent( IMediaContent ):
    channels = schema.Int( **d)
    creation_date = schema.Date( **d)
    album = schema.Text( **d)
    genre = schema.Text( **d)
    samplerate = schema.Int( **d )
    length = schema.ASCIILine( **d)
    encoder = schema.ASCIILine( **d)
    codec = schema.ASCIILine( **d)
    bitrate = schema.Float( **d)
    language = schema.TextLine( **d)

class IMP3Content( IAudioContent ):
    """ special marker for mp3, because we provide r/w for against the file """

class IVideoContent( IMediaContent ):
    length = schema.Int( **d)
    caption = schema.TextLine( **d)
    height = schema.Int( **d)
    width = schema.Int( **d)
    fps = schema.Int( **d)
    aspect = schema.ASCIILine( **d)
    
class IPhotoContent( IMediaContent ):
    location = schema.Text( **d)
    event = schema.Text( **d)
    width = schema.Int( **d)
    height = schema.Int( **d)
    software = schema.Text( **d)
    hardware = schema.Text( **d)
    dpi = schema.Int( **d)

class IOfficeContent( IMimeTypeProperties ):
    # creator, language, template, title, generator, last saved by, company
    company = schema.Text( **d )
    template = schema.Text( **d )
    generator = schema.Text( **d )
    last_saved_by = schema.Text( **d )
    software = schema.Text( **d )
    
    # author, software, creata
