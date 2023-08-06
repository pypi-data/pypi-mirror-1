"""Test suite for python examples embedded in the documentation"""
import os
import doctest

def test_suite():
    # Locate the doc/src directory relative to the current file.
    test_dir = os.path.dirname(os.path.abspath(__file__))
    brainfreeze_dir = os.path.dirname(test_dir)
    doc_dir = os.path.join(brainfreeze_dir, 'doc', 'src')
    
    # Walk the doc/src tree and locate all the .txt files
    doc_files = []
    for root, dirs, files in os.walk(doc_dir):
        for name in files:
            if name.endswith('.txt'):
                path = os.path.join(root, name)
                doc_files.append(path)

    kw = dict(module_relative=False)
    return doctest.DocFileSuite(*doc_files, **kw)

if __name__ == '__main__':
    import sys
    import unittest
    if sys.version_info[:2] < (2, 4):
        print "Python 2.4 or later required for tests (%d.%d detected)." % \
            sys.version_info[:2]
        sys.exit(-1)
    unittest.TextTestRunner().run(test_suite())
    

