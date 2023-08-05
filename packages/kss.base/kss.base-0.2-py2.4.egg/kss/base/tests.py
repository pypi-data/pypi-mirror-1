import unittest
import doctest

def test_suite():
    suite = unittest.TestSuite((
        doctest.DocFileSuite(
            'README.txt', 'selectors.txt',
            'registry.txt', 'plugin.txt',
            'commands.txt', 'corecommands.txt',
            'javascript.txt',
            package='kss.base',
            optionflags=doctest.ELLIPSIS|doctest.REPORT_ONLY_FIRST_FAILURE,
        ),
    ))
    return suite
