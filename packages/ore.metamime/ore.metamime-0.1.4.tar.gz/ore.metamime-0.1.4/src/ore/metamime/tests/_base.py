import unittest, os

from zope.component.testing import setUp, tearDown
from zope.filerepresentation.interfaces import IReadFile

import ore.metamime

libdir  = os.path.abspath( os.path.join( os.path.dirname( ore.metamime.__file__) ) )
datadir = os.path.abspath( os.path.join( os.path.dirname( __file__ ) , 'data') )

from zope import component, interface

from ore.metamime import interfaces



class file( file ):
    interface.implements( IReadFile )

class MimeTest( unittest.TestCase ):

    def setUp( self ):
        setUp()
        

    def tearDown( self ):
        tearDown()
