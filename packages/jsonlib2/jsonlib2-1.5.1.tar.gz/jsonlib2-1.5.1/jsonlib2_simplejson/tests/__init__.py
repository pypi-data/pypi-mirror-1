import unittest
import doctest

def additional_tests():
    import jsonlib2
    import sys
    sys.modules['simplejson'] = jsonlib2
    simplejson =  jsonlib2
    suite = unittest.TestSuite()
    return suite

def main():
    suite = additional_tests()
    runner = unittest.TextTestRunner()
    runner.run(suite)

if __name__ == '__main__':
    import os
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    main()
