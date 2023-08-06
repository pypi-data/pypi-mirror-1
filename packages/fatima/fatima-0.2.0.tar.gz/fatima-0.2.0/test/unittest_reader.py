"""unittest for the IM test client

FIXME: - valeurs aleatoires (hi, hello...)
       - valeurs dependantes de la config du narval (help)
"""

__revision__ = '$Id: unittest_reader.py,v 1.5 2005-05-17 08:06:54 arthur Exp $'

import unittest
from logilab.common import testlib

from fatima.dialog import Dialog
from fatima.reader import *


SAMPLE = """=====================
 Narval User Stories
=====================

A Narval agent can connect to a jabber server to exchange messages
and presence information using XMPP_. Here are user stories describing the
interaction between a Narval and a user.

.. _XMPP: http://www.jabber.org/protocol/


hello world
-----------

Let us begin with the simplest example of all. We have an agent named gizmo and
a user named Jean.

Test ::

  DIALOG(jean,gizmo)

  jean: hello
  gizmo: hi



Note-taking
-----------

We are chatting with a Narval agent and we want it to remember some
of what we say. It could be for example that it records every sentence
that contains the word 'action'.

Test ::

     DIALOG(jean,gizmo)

     jean: hi
     gizmo: hi
     jean: It is a nice day.
     jean: action: I will go for a hike.
     jean: and try not to forget my backpack
     jean: tell me about action
     gizmo: jean: "action: I will go for a hike."
     jean: tell me about backpack
     gizmo: nothing known about backpack.
     jean: tell me about hike
     gizmo: jean "action: I will go for a hike."



Set-up jabber meeting
---------------------

Jean asks his agent to set up a jabber meeting. Gizmo opens a forum
and invites participants.

Test ::


     DIALOG(jean,gizmo)

     jean: set up conference agents with gizmo jean paul
     gizmo: ok
     
     FORUM(agents,jean,gizmo)
     [gizmo invites jean to forum agents]
     [jean accepts invitation to forum agents]
     [gizmo is present in forum agents]
     jean: gizmo: thanks
     gizmo: jean: you are welcome

Test the noTest thing
---------------------

Description of the test

noTest ::


     DIALOG(jean,gizmo)

     jean: set up conference agents with gizmo jean paul
     gizmo: ok
     

"""
     
class ReSTDialogReaderTC(testlib.TestCase):

    def setUp(self):
        self.reader = ReSTDialogReader()
        
    def test_extract_sections(self):
        sections = list(self.reader.extract_sections(SAMPLE))
        self.assertListEquals(sections,
                          [

            (3, 1, ' Narval User Stories', '''A Narval agent can connect to a jabber server to exchange messages
and presence information using XMPP_. Here are user stories describing the
interaction between a Narval and a user.

.. _XMPP: http://www.jabber.org/protocol/'''),


            (13, 2, 'hello world',
'''Let us begin with the simplest example of all. We have an agent named gizmo and
a user named Jean.

Test ::

  DIALOG(jean,gizmo)

  jean: hello
  gizmo: hi'''),
                           (28, 2, 'Note-taking',
'''We are chatting with a Narval agent and we want it to remember some
of what we say. It could be for example that it records every sentence
that contains the word 'action'.

Test ::

     DIALOG(jean,gizmo)

     jean: hi
     gizmo: hi
     jean: It is a nice day.
     jean: action: I will go for a hike.
     jean: and try not to forget my backpack
     jean: tell me about action
     gizmo: jean: "action: I will go for a hike."
     jean: tell me about backpack
     gizmo: nothing known about backpack.
     jean: tell me about hike
     gizmo: jean "action: I will go for a hike."'''),
                           (53, 2, 'Set-up jabber meeting',
'''Jean asks his agent to set up a jabber meeting. Gizmo opens a forum
and invites participants.

Test ::


     DIALOG(jean,gizmo)

     jean: set up conference agents with gizmo jean paul
     gizmo: ok
     
     FORUM(agents,jean,gizmo)
     [gizmo invites jean to forum agents]
     [jean accepts invitation to forum agents]
     [gizmo is present in forum agents]
     jean: gizmo: thanks
     gizmo: jean: you are welcome'''),
                           (74, 2,'Test the noTest thing',
'''Description of the test

noTest ::


     DIALOG(jean,gizmo)

     jean: set up conference agents with gizmo jean paul
     gizmo: ok'''),
                           ])
        
    def test_dialog_from_section(self):
        dlg = self.reader.dialog_from_section('Set-up jabber meeting',
'''Jean asks his agent to set up a jabber meeting. Gizmo opens a forum
and invites participants.

Test ::


     DIALOG(jean,gizmo)

     jean: set up conference agents with gizmo jean
           paul
     gizmo: ok

     
     FORUM(agents,jean,gizmo)
     [gizmo invites jean to forum agents]
     [jean accepts invitation to forum agents]
     [gizmo is present in forum agents]
     jean: gizmo: thanks
     gizmo: jean: you are welcome
''')
        self.assertEquals(dlg.title, 'Set-up jabber meeting')
        self.assertEquals(dlg.description, '''Jean asks his agent to set up a jabber meeting. Gizmo opens a forum
and invites participants.
''')
        self.assertEquals(len(dlg.actions), 9)
                          
        
    def test_from_string(self):
        dlgs = list(self.reader.from_string(SAMPLE))
        self.assertEquals(len(dlgs), 5)
        self.assertEquals(len([dlg for level, dlg in dlgs if isinstance(dlg, Dialog)]), 5)


class AliasesReaderTC(testlib.TestCase):
    
    def setUp(self):
        self.reader = AliasesReader()

    def test_from_string(self):
        aliases = self.reader.from_string("""
# a comment
hi = hello, bonjour, yo
  'lo
  
bye = see you, au revoir, a+
""")
        self.assertEquals(aliases, {'hi': ['hi', 'hello', 'bonjour', 'yo', "'lo"],
                                    'bye': ['bye', 'see you', 'au revoir', 'a+']})
                          
    
if __name__ == '__main__':
    unittest.main()
