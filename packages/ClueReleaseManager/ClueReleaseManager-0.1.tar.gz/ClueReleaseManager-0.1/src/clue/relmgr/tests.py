import unittest
import doctest
import logging
from clue.relmgr import utils


def test_suite():
    logging.basicConfig()
    utils.logger.setLevel(logging.ERROR)

    flags = doctest.ELLIPSIS
    suite = unittest.TestSuite()
    suite.addTest(doctest.DocTestSuite('clue.relmgr.server',
                                       optionflags=flags))
    suite.addTest(doctest.DocTestSuite('clue.relmgr.model',
                                       optionflags=flags))

    return suite


def main():
    runner = unittest.TextTestRunner()
    runner.run(test_suite())


if __name__ == '__main__':
    main()
