# Unit tests for reflex

import unittest
import reflex

class TestScannerCreate( unittest.TestCase ):
    
    def setUp( self ):
        self.scanner = reflex.scanner( "start" )
        
    def test_state( self ):
        self.assertEqual( self.scanner.build_state.name, "start" )

    def test_state( self ):
        self.assertEqual( self.scanner.start_state.name, "start" )

class TestScannerRule( unittest.TestCase ):
    
    def setUp( self ):
        self.scanner = reflex.scanner( "start" )
        self.scanner.rule( "\s+" )
        
    def test_rule( self ):
        self.assertEqual( len( self.scanner.build_state.rules ), 1 )

class TestScannerScan( unittest.TestCase ):
    
    def setUp( self ):
        self.scanner = reflex.scanner( "start" )
        self.scanner.rule( "\s+" )
        self.scanner.rule( "[a-z]+", token="letters" )
        self.scanner.rule( "[0-9]+", token="numbers" )
        self.stream = self.scanner(
            iter( [ "    abc 123 456anywhere\n",
                    "    abc 123 456anywhere\n" ] ) )
        self.tokens = list( self.stream )
        
    def test_token_count( self ):
        self.assertEqual( len( self.tokens ), 8 )
    
    def test_token_types( self ):
        self.assertEqual( self.tokens[ 0 ].id, "letters" )
        self.assertEqual( self.tokens[ 1 ].id, "numbers" )
        self.assertEqual( self.tokens[ 2 ].id, "numbers" )
        self.assertEqual( self.tokens[ 3 ].id, "letters" )
        self.assertEqual( self.tokens[ 4 ].id, "letters" )
        self.assertEqual( self.tokens[ 5 ].id, "numbers" )
        self.assertEqual( self.tokens[ 6 ].id, "numbers" )
        self.assertEqual( self.tokens[ 7 ].id, "letters" )

    def test_token_values( self ):
        self.assertEqual( self.tokens[ 0 ].value, "abc" )
        self.assertEqual( self.tokens[ 1 ].value, "123" )
        self.assertEqual( self.tokens[ 2 ].value, "456" )
        self.assertEqual( self.tokens[ 3 ].value, "anywhere" )
        self.assertEqual( self.tokens[ 4 ].value, "abc" )
        self.assertEqual( self.tokens[ 5 ].value, "123" )
        self.assertEqual( self.tokens[ 6 ].value, "456" )
        self.assertEqual( self.tokens[ 7 ].value, "anywhere" )

def suite():
    """ Create the test suite for this module """
    from sys import modules
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule( modules[__name__] )
    return suite

if __name__ == '__main__':
    unittest.main()
