import unittest
import doctest

modules = [
    'chimera.chimera',
    'chimera.utils',
    'chimera.colors',
    ]



def test_suite():
    g = globals()
    suite = unittest.TestSuite()
    for module in modules:
        try:
            mobj = __import__(module, g, g, module.split('.', 1)[1])
        except IndexError, E:
            mobj = __import__(module, g, g, None)

        suite.addTest(doctest.DocTestSuite(mobj))

    return suite

if __name__ == "__main__":
    runner = unittest.TextTestRunner()
    runner.run(test_suite())




