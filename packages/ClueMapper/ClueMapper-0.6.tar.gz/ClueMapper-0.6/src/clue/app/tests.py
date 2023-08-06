import unittest
import doctest
import os
import logging


def test_suite():
    flags = doctest.ELLIPSIS

    os.environ['cluemapper.loglevel'] = str(logging.FATAL)
    suite = unittest.TestSuite()
    suite.addTest(doctest.DocTestSuite('clue.app.admin',
                                       optionflags=flags))
    suite.addTest(doctest.DocTestSuite('clue.app.config',
                                       optionflags=flags))
    suite.addTest(doctest.DocTestSuite('clue.app.controller',
                                       optionflags=flags))
    suite.addTest(doctest.DocTestSuite('clue.app.environinit',
                                       optionflags=flags))
    suite.addTest(doctest.DocTestSuite('clue.app.patches',
                                       optionflags=flags))
    suite.addTest(doctest.DocTestSuite('clue.app.pdbcheck',
                                       optionflags=flags))
    suite.addTest(doctest.DocTestSuite('clue.app.project',
                                       optionflags=flags))
    suite.addTest(doctest.DocTestSuite('clue.app.redirect',
                                       optionflags=flags))
    suite.addTest(doctest.DocTestSuite('clue.app.server',
                                       optionflags=flags))
    suite.addTest(doctest.DocTestSuite('clue.app.utils',
                                       optionflags=flags))
    suite.addTest(doctest.DocFileSuite('cluemapper.txt',
                                       package='clue.app',
                                       optionflags=flags))
    return suite


def main():
    runner = unittest.TextTestRunner()
    runner.run(test_suite())

if __name__ == '__main__':
    main()
