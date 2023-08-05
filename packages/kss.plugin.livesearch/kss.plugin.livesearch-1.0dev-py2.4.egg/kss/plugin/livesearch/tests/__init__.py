import unittest
import doctest

def test_suite():
    suite = unittest.TestSuite((
        doctest.DocFileSuite(
            'README.txt',
            package='kss.plugin.livesearch',
            optionflags=doctest.ELLIPSIS|doctest.REPORT_ONLY_FIRST_FAILURE,
        ),
    ))
    return suite
