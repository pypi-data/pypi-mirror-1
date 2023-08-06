"""unittest for the jabber part of the IM test client
"""

__revision__ = '$Id: unittest_cli.py,v 1.2 2005-06-24 09:22:22 nico Exp $'

import unittest
from logilab.common import testlib

from fatima.imtestcli import *
from StringIO import StringIO

EXAMPLE = """
hello
*****
"""

class FatimaRunnerTC(testlib.TestCase):

    def setUp(self) :
        _input = StringIO()
        cfg = Configuration(options=OPTIONS, name='IM TEST',
                            usage=__doc__, doc="FATIMA's configuration file")
        cfg['password'] = 'toto'
        self.f = FatimaRunner('toto', _input, cfg, verbose=False)
        
    def test_one(self) :
        self.f.run(StringIO())

    
class WriterTC(testlib.TestCase):

    def test_htmlwriter(self) :
        document = Section()
        writer = get_writer('html')
        writer.format(document, StringIO())

if __name__ == '__main__':
    unittest.main()
