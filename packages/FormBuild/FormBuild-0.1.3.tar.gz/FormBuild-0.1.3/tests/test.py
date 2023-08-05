import unittest, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(1, '../')

from test_field import TestFieldsSimpleHTML, TestFieldsCompoundHTML

if __name__ == '__main__':
    suite = [unittest.makeSuite(TestFieldsSimpleHTML)]
    suite.append(unittest.makeSuite(TestFieldsCompoundHTML))
    for testsuite in suite:
        unittest.TextTestRunner(verbosity=1).run(testsuite)
        
    import doctest
    doctest.testfile("../docs/manual.txt")
    raw_input('All done. Press ENTER to end.')