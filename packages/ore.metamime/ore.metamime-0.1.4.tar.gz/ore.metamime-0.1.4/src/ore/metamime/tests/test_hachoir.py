"""
$Id: test_hachoir.py 2259 2008-11-04 22:17:36Z hazmat $
"""

import os
from unittest import TestSuite, makeSuite, main
from _base import MimeTest, datadir, file

#from hachoir_core import error
#error.warning = None

from zope import component
from zope.filerepresentation.interfaces import IReadFile

from ore.metamime import interfaces, hachoir

class HachoirMimeTest( MimeTest ):

    def setUp( self ):
        super( HachoirMimeTest, self).setUp()
        component.provideAdapter( hachoir.HachoirFileClassifier,
                                  adapts=( IReadFile, ),
                                  provides=interfaces.IMimeClassifier )
                                  
        component.provideAdapter( hachoir.HachoirMetadataExtractor,
                                  adapts=( IReadFile, ),
                                  provides=interfaces.IMimeMetadataExtractor )

        
class TestFileClassification( HachoirMimeTest ):

    def test_ClassifyMP3(self):
        fh = file( os.path.join(datadir, 'data.mp3') )
        classifer =interfaces.IMimeClassifier(fh)
        self.assertEqual( classifer.queryMimeType(), 'audio/mpeg')

    def test_ClassifyGif(self):
        fh = file( os.path.join(datadir, 'data.gif') )
        classifer = interfaces.IMimeClassifier(fh)
        self.assertEqual( classifer.queryMimeType(), 'image/gif')        

    def test_ClassifyPDF( self ):
        fh = file( os.path.join(datadir, 'data.pdf' ) )
        classifer = interfaces.IMimeClassifier(fh)
        self.assertEqual( classifer.queryMimeType(), 'application/pdf')

class TestFileExtraction( HachoirMimeTest ):

    def test_ExtractMP3(self):
        fh = file( os.path.join(datadir, 'data.mp3') )
        extractor = interfaces.IMimeMetadataExtractor(fh)
        d = extractor.extract()
        self.assertEqual( d['music_genre'], 'Podcast' )
        self.assertEqual( d['bit_rate'], 64000 )

    def test_ExtractGif(self):
        fh = file( os.path.join(datadir, 'data.gif') )
        extractor = interfaces.IMimeMetadataExtractor(fh)

        d = extractor.extract()
        self.assertEqual( d[u'height'], 114 )
        self.assertEqual( d[u'width'], 332 )

    def test_ExtractPDF( self ):
        fh = file( os.path.join(datadir, 'data.pdf' ) )
        extractor = interfaces.IMimeMetadataExtractor(fh)
        d = extractor.extract()
        # hachoir doesn't extract anything useful from pdfs
        #print ""*100
        #print d
        
def test_suite():
    suite = TestSuite()
    suite.addTest( makeSuite(TestFileClassification) )
    suite.addTest( makeSuite(TestFileExtraction ) )
    return suite    

if __name__ == '__main__':
    main()
