------------
ore.metamime
------------

A python library for the mime based behaviors and attributes, w

we use mime types as a means of classiying content, extracting metadata, transforming
content, querying icons, and attaching component architecture based behavior to content 
based on mimetype.

we provide fast, useful default behavior out of the box by relying on libextractor for 
classification and metadata with the ability to customize behavior for any mimetype.

Utility
-------

we use a utility as a facade for internal adapters to present a high level interface with
overrideable local implementations backing to the global default behavior. It provides
interfaces for classifying a content's mimetype, extraction and application of file content
metadata.

Usage
-----

  >> utility = getUtility( IMimeUtility )

  # to attach a mime type to a content 
  >> utility.classify( content )

  # to extract metadata and update the file properties
  >> utility.extractAndApply( content )

  >> dc = IWriteZopeDublinCore( content )
  >> dc.title

  # we defer extracted generic properties to the mime content object
  # and mime specific behavior as well.

  # to inspect the mime content properties and 
  >> mime = utility.getMimeContent( content )

  # defined key value pairs specific to the mime
  mime.values()
  mime.keys()

to extract and apply metadata

Internals
---------

we define multiple components for each mime type

 - [a] a named adapter for *, IMimeType, mime type that returns an object implementing
       mime specific behavior and with mime specific attributes.
 - [c] a marker sub interface of IMimeType specific to the mime type
 - [d] a mime object interface
 - [c] a mime object implementation
 
we define adapters for additional capabilities with default adapters for file classification,
extraction, and a generic mime object implementation. any of these can customized for a given
mime type. adapters are also used for transformation capabilities, however no default 
implementations are currently provided.

 - [d] a metadata extractor registered for a specific IMimeType
 - [d] a metadata classifier registered for
 - an optional metadata transformer adapter for a specific interface
 - utilities for getting a specific IMimeType by name

mimes which want to implement mutation of properties back to files need to
register a named adapter to their mime object interface from the marker interface. 
the generic extractor is meant to be easily customized to map extracted terms to specific
schema fields via mapping mutation. 

we generate default code and zcml for mime types using the included generator.py

 context based
 
 - getting the mime specific property schema
 - getting the configurable values of a mime on an instance

 

Futures

default behavior

cached mime data for easy access ( icon comes to mind )

delegated fieldproperty for deferring metadata fields to other schemas
 
distinguish mutation in watchers with revision properties

svn file open method returns file like object ( seek, read, write )

 - metadata classification( async )
 
 - media transforms (async)

   - drop in directory and drop in directory

  some object views depend upon transformations, if so they are based on container applied
  marker interfaces.

  # named transformation adapters... no state based transformed adapters
  TransformedView( ):

  def getTransformed( ):
      pass
   
class metadata
class mime classifier
class mime metadata extractor

libextractor

 
Mime hierarchy

FileMimeType

  - Office
     - OpenOffice
     - Microsoft
     
  - Media           
     - Audio
     - Video
     - Photo
     
  - Text
     - S5
     - Source
     - RestructuredTExt
     - HTML
     - Wiki
     - XML
     - CSS
     - CSV
     - ICAL

DirectoryMimeType / Behavior

 pre build directory structure

  - Default File Mime ( Rule For Interface Application )

  - Recursive Mime (File and Directories)

  - Blog

  - Media Album

  - Book

Directory Behaviors / Rules

  - set interface
  - transform
  - apply order
  - apply workflow 
  - apply versioning


File Behaviors
  - Indexed


SubversionBlob

Configured Views

For app specific text types  have an external editor app mapping.
