import unittest

import test_classify
import test_extractor

def test_suite():
    suite = unittest.TestCase()
    for mod in [ test_classify, test_extractor ]:
        suite.addTests( mod.test_suite() )
    return suite

def main():
    runner = unittest.TextTestRunner( verbosity = 2)
    result = runner.run( test_suite() )

if __name__ == '__main__':
    main()
    

    
