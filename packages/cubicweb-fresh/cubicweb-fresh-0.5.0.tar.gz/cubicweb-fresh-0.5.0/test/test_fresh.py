"""template automatic tests"""

from logilab.common.testlib import unittest_main

from cubicweb.devtools.htmlparser import SaxOnlyValidator
from cubicweb.devtools.testlib import AutomaticWebTest

AutomaticWebTest.vid_validators.update({
    'accexpense': SaxOnlyValidator,
    'accentry': SaxOnlyValidator,
    })

if __name__ == '__main__':
    unittest_main()
