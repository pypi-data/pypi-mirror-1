"""unittest for the jabber part of the IM test client
"""

__revision__ = '$Id: unittest_jabber.py,v 1.3 2005-04-13 12:51:19 syt Exp $'

import unittest
from logilab.common import testlib

from fatima import dialog
from fatima.jabber import *


class JabberAdapterTC(testlib.TestCase):

    def setUp(self):
        self.adapter = JabberAdapter()
        self.adapter.client = TwistedJabberClient(None, 'jabber.logilab.org', 'tim', None)

        
    def test_message2twxml(self):
        adapter = self.adapter
        adapter.set_context(dialog.Context('chat', 'tim', 'bot'))
        twxml = adapter.action2twxml(dialog.SendMessage('bot', 'content'))
        self.assertEquals(twxml.toXml(),
                          "<message to='bot@jabber.logilab.org' \
type='chat' from='tim@jabber.logilab.org/imtest'>\
<body>content</body></message>")
        adapter.context = dialog.Context('forum', 'tim', 'bot', 'agents')
        twxml = adapter.action2twxml(dialog.SendMessage('bot', 'content'))
        self.assertEquals(twxml.toXml(),
                          "<message to='agents@conference.jabber.logilab.org' \
type='groupchat' from='agents@conference.jabber.logilab.org/tim'>\
<body>content</body></message>")


    
    def test_presence2twxml(self):
        adapter = self.adapter
        adapter.set_context(dialog.Context('chat', 'tim', 'bot'))
        twxml = self.adapter.action2twxml(dialog.SendPresence('bot', 'content'))
        self.assertEquals(twxml.toXml(),
                          """<presence to='bot@jabber.logilab.org' \
from='tim@jabber.logilab.org/imtest'/>""")
        adapter.context = dialog.Context('forum', 'tim', 'bot', 'agents')
        twxml = self.adapter.action2twxml(dialog.SendPresence('bot', 'content'))
        self.assertEquals(twxml.toXml(),
                          """<presence to='agents@conference.jabber.logilab.org/tim' \
from='tim@jabber.logilab.org/imtest'/>""")


    
    def test_sendinvitation2twxml(self):
        adapter = self.adapter
        adapter.set_context(dialog.Context('chat', 'tim', 'bot'))
        twxml = self.adapter.action2twxml(dialog.SendInvitation('bot', 'content'))
        self.assertEquals(twxml.toXml(),
                          "<message to='bot@jabber.logilab.org' \
type='normal' from='tim@jabber.logilab.org/imtest'>\
<body>You are invited to content by tim</body>\
<x jid='content' xmlns='jabber:x:conference'/>\
</message>")
        adapter.context = dialog.Context('forum', 'tim', 'bot', 'agents')
        twxml = self.adapter.action2twxml(dialog.SendInvitation('bot', 'content'))
        self.assertEquals(twxml.toXml(),
                          "<message to='bot@jabber.logilab.org' \
type='normal' from='tim@jabber.logilab.org/imtest'>\
<body>You are invited to content by tim</body>\
<x jid='content' xmlns='jabber:x:conference'/>\
</message>")


        
    def test_acceptinvitation2twxml(self):
        adapter = self.adapter
        adapter.set_context(dialog.Context('chat', 'tim', 'bot'))
        twxml = self.adapter.action2twxml(dialog.AcceptInvitation('whatever', 'content'))
        self.assertEquals(twxml.toXml(),
                          "<presence to='content@conference.jabber.logilab.org/tim' from='tim@jabber.logilab.org/imtest'/>")
        adapter.context = dialog.Context('forum', 'tim', 'bot', 'agents')
        twxml = self.adapter.action2twxml(dialog.AcceptInvitation('whatever', 'content'))
        self.assertEquals(twxml.toXml(),
                          "<presence to='content@conference.jabber.logilab.org/tim' from='tim@jabber.logilab.org/imtest'/>")
    

if __name__ == '__main__':
    unittest.main()
