
import unittest

import test_Node
import test_File
import test_Directory
import test_Properties
import test_Transaction

def test_suite():
    suite = unittest.TestSuite()
    for mod in [ test_Node, test_File, test_Directory, test_Properties, test_Transaction ]:
        suite.addTests( mod.test_suite() )
    return suite

def main():
    runner = unittest.TextTestRunner( verbosity = 2)
    result = runner.run( test_suite() )

if __name__ == '__main__':
    main()
    
        
        
