"""unittest for the IM test client

FIXME: - valeurs aleatoires (hi, hello...)
       - valeurs dependantes de la config du narval (help)
"""

__revision__ = '$Id: unittest_dialog.py,v 1.3 2005-05-20 14:20:11 arthur Exp $'

import unittest
from logilab.common import testlib

from fatima.dialog import *

class DialogTC(testlib.TestCase):

    def setUp(self):
        self.dlg = Dialog('title', 'description')

    def test_base(self):
        dlg = self.dlg
        self.assertEquals(dlg.title, 'title')
        self.assertEquals(dlg.description, 'description')
        self.assertEquals(dlg.actions, [])
        self.assertEquals(dlg.current_context, None)
        
    def test_action_string(self):
        dlg = self.dlg
        dlg.action_string('DIALOG(jean, gizmo)')
        self.assertEquals(len(dlg.actions), 1, dlg)
        action = dlg.actions[-1]
        self.assertEquals(isinstance(action, Context), True)
        self.assertEquals(action, dlg.current_context)
        self.assertEquals(action.name, 'chat')
        self.assertEquals(action.user_nick, 'jean')
        self.assertEquals(action.bot_nick, 'gizmo')
        
        dlg.action_string('FORUM(agents, jean, gizmo)')
        self.assertEquals(len(dlg.actions), 2, dlg)
        action = dlg.actions[-1]
        self.assertEquals(isinstance(action, Context), True)
        self.assertEquals(action, dlg.current_context)
        self.assertEquals(action.name, 'forum')
        self.assertEquals(action.user_nick, 'jean')
        self.assertEquals(action.bot_nick, 'gizmo')
        self.assertEquals(action.more_info, ('agents',))

        self.assertRaises(BadDialog, dlg.action_string, 'unknown: hi')
        
        dlg.action_string('jean: hi')
        self.assertEquals(len(dlg.actions), 3, dlg)
        action = dlg.actions[-1]
        self.assertEquals(isinstance(action, SendMessage), True)
        self.assertEquals(action.nick, 'jean')
        self.assertEquals(action.content, 'hi')
        
        dlg.action_string('gizmo: hello')
        self.assertEquals(len(dlg.actions), 4)
        action = dlg.actions[-1]
        self.assertEquals(isinstance(action, ReceiveMessage), True)
        self.assertEquals(action.nick, 'gizmo')
        self.assertEquals(action.content, 'hello')
        
        dlg.action_string('[gizmo invites jean to forum agents]')
        self.assertEquals(len(dlg.actions), 5)
        action = dlg.actions[-1]
        self.assertEquals(isinstance(action, ReceiveInvitation), True)
        self.assertEquals(action.nick, 'gizmo')
        self.assertEquals(action.content, 'agents')
     
        dlg.action_string('[jean accepts invitation to forum agents]')
        self.assertEquals(len(dlg.actions), 6)
        action = dlg.actions[-1]
        self.assertEquals(isinstance(action, AcceptInvitation), True)
        self.assertEquals(action.nick, 'jean')
        self.assertEquals(action.content, 'agents')
     
        dlg.action_string('[gizmo is present in forum agents]')
        self.assertEquals(len(dlg.actions), 7)
        action = dlg.actions[-1]
        self.assertEquals(isinstance(action, ReceivePresence), True)
        self.assertEquals(action.nick, 'gizmo')
        self.assertEquals(action.content, 'agents')

        dlg.action_string('gizmo:{re} test .* regex')
        action= dlg.actions[-1]
        other = IMAction('gizmo', 'test this regex')
        self.assertEquals(action.is_equivalent(other), True)

        dlg.action_string('gizmo:{re} test .* regex')
        action= dlg.actions[-1]
        other = IMAction('gizmo', '''test this
        multiline regex''')
        self.assertEquals(action.is_equivalent(other), True)


if __name__ == '__main__':
    unittest.main()
