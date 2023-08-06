import unittest
import doctest


def test_suite():
    flags = doctest.ELLIPSIS

    suite = unittest.TestSuite()
    suite.addTest(doctest.DocTestSuite('clue.secure.auth',
                                       optionflags=flags))
    suite.addTest(doctest.DocTestSuite('clue.secure.htpasswd',
                                       optionflags=flags))
    return suite


def main():
    runner = unittest.TextTestRunner()
    runner.run(test_suite())

if __name__ == '__main__':
    main()
