# Copyright 2007, Blue Dynamics Alliance, Austria - www.bluedynamics.com
#
# GNU General Public Licence Version 2 or later 
#
__author__ = """Jens Klein <jens@bluedynamics.com>"""

import unittest
import doctest

def test_suite():
    optionflags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
    return unittest.TestSuite((
        doctest.DocFileSuite('serializer.py',
                             package='xmlpolymerase',
                             optionflags=optionflags),
        doctest.DocFileSuite('deserializer.py',
                             package='xmlpolymerase',
                             optionflags=optionflags),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
