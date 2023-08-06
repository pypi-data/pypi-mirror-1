"""
$Id: test_libextractor.py 2259 2008-11-04 22:17:36Z hazmat $
"""

import os
from unittest import TestSuite, makeSuite, main
from _base import MimeTest, datadir, file

from zope import component
from zope.filerepresentation.interfaces import IReadFile

from ore.metamime import interfaces, libextractor

class ExtractorMimeTest( MimeTest ):
    
    def setUp( self ):
        super( ExtractorMimeTest, self).setUp()
        
        component.provideAdapter( libextractor.ExtractorFileClassifier,
                                  adapts=( IReadFile, ),
                                  provides=interfaces.IMimeClassifier,
                                  name="libextractor")
        component.provideAdapter( libextractor.ExtractorMetadataExtractor,
                                  adapts=( IReadFile, ),
                                  provides=interfaces.IMimeMetadataExtractor,
                                  name="libextractor")
        
    



class TestFileClassification( MimeTest ):

    def test_ClassifyMP3(self):
        fh = file( os.path.join(datadir, 'data.mp3') )
        classifer = component.getAdapter( fh, interfaces.IMimeClassifier, "libextractor")
        self.assertEqual( classifer.queryMimeType(), 'audio/mpeg')

    def test_ClassifyGif(self):
        fh = file( os.path.join(datadir, 'data.gif') )
        classifer = component.getAdapter( fh, interfaces.IMimeClassifier, "libextractor")        
        self.assertEqual( classifer.queryMimeType(), 'image/gif')        

    def test_ClassifyPDF( self ):
        fh = file( os.path.join(datadir, 'data.pdf' ) )
        classifer = component.getAdapter( fh, interfaces.IMimeClassifier, "libextractor")
        self.assertEqual( classifer.queryMimeType(), 'application/pdf')

class TestFileExtraction( MimeTest ):

    def test_ExtractMP3(self):
        fh = file( os.path.join(datadir, 'data.mp3') )
        extractor = component.getAdapter( fh, interfaces.IMimeMetadataExtractor, "libextractor")
        d = extractor.extract()
        self.assertEqual( d['genre'], 'Podcast' )
        self.assertEqual( d['resource-type'], 'MPEG V25')

    def test_ExtractGif(self):
        fh = file( os.path.join(datadir, 'data.gif') )
        extractor = component.getAdapter( fh, interfaces.IMimeMetadataExtractor, "libextractor")
        d = extractor.extract()
        self.assertEqual( d[u'size'], u'332x114' )

    def test_ExtractPDF( self ):
        fh = file( os.path.join(datadir, 'data.pdf' ) )
        extractor = component.getAdapter( fh, interfaces.IMimeMetadataExtractor, "libextractor")
        d = extractor.extract()
        self.assertEqual( d['creator'], 'Writer')
                   
def test_suite():
    suite = TestSuite()
    suite.addTest( makeSuite(TestFileClassification) )
    suite.addTest( makeSuite(TestFileExtraction ) )
    return suite    

if __name__ == '__main__':
    main()
