import unittest
import doctest


def test_suite():
    flags = doctest.ELLIPSIS
    suite = unittest.TestSuite()
    suite.addTest(doctest.DocTestSuite('cluebin.paste',
                                       optionflags=flags))
    suite.addTest(doctest.DocTestSuite('cluebin.pastebin',
                                       optionflags=flags))
    suite.addTest(doctest.DocTestSuite('cluebin.utils',
                                       optionflags=flags))

    return suite


def main():
    runner = unittest.TextTestRunner()
    runner.run(test_suite())


if __name__ == '__main__':
    main()
