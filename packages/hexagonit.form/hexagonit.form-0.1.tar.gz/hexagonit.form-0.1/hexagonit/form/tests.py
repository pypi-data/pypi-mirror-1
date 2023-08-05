import unittest
from doctest import DocFileSuite, ELLIPSIS

def test_suite():
    return unittest.TestSuite((
        DocFileSuite('orderable.txt',
                     package='hexagonit.form.orderable',
                     optionflags=ELLIPSIS),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
