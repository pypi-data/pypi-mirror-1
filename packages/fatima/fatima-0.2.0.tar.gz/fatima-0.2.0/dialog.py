# Copyright (c) 2005 LOGILAB S.A. (Paris, FRANCE).
# http://www.logilab.fr/ -- mailto:contact@logilab.fr
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
"""classes to handle user <-> bot dialog control (messages and presences)
"""

__revision__ = '$Id: dialog.py,v 1.17 2005-06-24 10:03:44 nico Exp $'

import re
import time
import Queue

from logilab.common.textutils import colorize_ansi
from logilab.common.ureports.nodes import Table, Paragraph, Span
    
class BadDialog(Exception):
    """exception raised when a dialog is malformated or uses incorrect
    information (such as unknown user/bot nicks)
    """

DIALOG_RGX = re.compile('DIALOG\s*\(\s*'
                        '(?P<user_nick>\w+)'
                        '\s*,\s*'
                        '(?P<bot_nick>\w+)'
                        '\s*\)')

FORUM_RGX = re.compile('FORUM\s*\(\s*'
                       '(?P<forum_room>\w+)'
                       '\s*,\s*'
                       '(?P<user_nick>\w+)'
                       '\s*,\s*'
                       '(?P<bot_nick>\w+)'
                       '\s*\)')

SPECIAL_RGX = re.compile('\[\s*'
                         '(?P<initiator_nick>\w+)\s+'
                         '(?P<action>invites|accepts invitation|is present|quits)\s+'
                         '(?P<receiver_nick>\w+)?\s*'
                         '(in|to)?\s*forum\s+'
                         '(?P<forum>\w+)'
                         '\s*\]')


class Dialog:
    """a dialog is a set of actions with a title and an optional description
    providing information about what's tested by this dialog
    """
    
    def __init__(self, title, description=None, verbose=True):
        self.title = title
        self.description = description
        self.actions = []
        self.current_context = None
        self.verbose = verbose

    def __repr__(self):
        return '<dialog %s, at %s, actions: %r>' % (self.title, id(self),
                                                    self.actions)
    
    def action_string(self, string):
        """take a string possibly defining an action in t he dialog,
        and do whatever is need with it
        """
        string = string.strip()
        if string.startswith("DIALOG") or string.startswith("FORUM"):
            self.current_context = self.context_action(string)
            self.actions.append(self.current_context)
        elif string.startswith('['):
            self.actions.append(self.special_action(string))
        else:
            self.actions.append(self.message_action(string))

    def context_action(self, string):
        """parse context information actions: 'DIALOG(user, bot)' and
        'FORUM(room, user, bot)'
        """
        if string.startswith("DIALOG"):
            match = DIALOG_RGX.match(string)
            return Context('chat',
                           match.group('user_nick'),
                           match.group('bot_nick'))
        else: #if string.startswith("FORUM"):
            match = FORUM_RGX.match(string)
            return Context('forum',
                           match.group('user_nick'),
                           match.group('bot_nick'),
                           match.group('forum_room'))
            
    def special_action(self, string):
        """parse special actions, surrounded by square brackets: '[...]')
        """
        if self.verbose :
            print string
        match = SPECIAL_RGX.match(string)
        context = self.current_context
        initiator = match.group('initiator_nick')
        action = match.group('action')
        forum = match.group('forum')
        receiver = match.group('receiver_nick')
        if action == 'invites':
            if initiator == context.user_nick and receiver == context.bot_nick:
                return SendInvitation(initiator, forum)
            elif initiator == context.bot_nick and receiver == context.user_nick:
                return ReceiveInvitation(initiator, forum)
            else:
                raise BadDialog('unknown nick: %s or %s' % (initiator, receiver))
        elif action == 'accepts invitation':
            if initiator == context.user_nick:
                # FIXME: send presence ?
                return AcceptInvitation(initiator, forum)
            elif initiator == context.bot_nick:
                # FIXME: send presence ?
                return ReceivePresence(initiator, forum)
            else:
                raise BadDialog('unknown nick: %s' % (initiator,))
        elif action == 'is present':
            if initiator == context.bot_nick:
                # FIXME: send presence ?
                return ReceivePresence(initiator, forum)
            else:
                msg = 'bad event: user %s don\'t receive its own presence...'
                raise BadDialog(msg % (initiator,))
        elif action == 'quits':
            if initiator == context.bot_nick:
                # FIXME: send presence ?
                return ReceiveQuitForum(initiator, forum)
            else:
                return QuitForum(initiator, forum)
        raise RuntimeError('duh ? %r' % string)

    def message_action(self, string):
        """parse message actions: 'user: msg'"""
        context = self.current_context
        optional = False
        if string.startswith('(') and string.endswith(')'):
            string = string[1:-1]
            optional = True
        from_name, msg = string.split(':', 1)
        if from_name == context.user_nick:
            msg = SendMessage(from_name, msg)
            msg.optional = optional
            return msg
        elif from_name == context.bot_nick:
            msg = ReceiveMessage(from_name, msg)
            msg.optional = optional
            return msg
        else:
            raise BadDialog('unknown nick: %s' % from_name)
        raise RuntimeError('duh ? %r' % string)


class DialogAction:
    """base class for every possible actions in a dialog"""
    def __str__(self):
        return repr(self)[1:-1]
    
class IMAction(DialogAction):
    """base class for im related actions in a dialog"""
    def __init__(self, nick, content=None):
        self.nick = nick
        self.content = content and content.strip()
        self.optional = False
        
    def __repr__(self):
        return '<%s: %s / %s>' % (self.__class__.__name__,
                                  self.nick, self.content)

    def add_content(self, line):
        """add another line of content (used when the action is defined with
        multiple lines in the source
        """
        self.content = '%s %s' % (self.content, line.strip())
        
    def is_equivalent(self, other, aliases=None):
        """return true if the other action is equivalent to self"""
        if aliases is None :
            aliases = {}
        return self.nick == other.nick and self.has_same_content(other, aliases)
    
    def has_same_content(self, other, aliases):
        """return true if the other action has an equivalent content,
        considering aliases"""
        try:
            return other.content.replace('\n',';') in aliases[self.content]
        except KeyError:
            if self.content.strip().startswith('{re}'):
                return re.match(self.content[4:].strip(),
                            other.content.replace('\n',';').strip()) is not None
            else:
                return self.content.strip() == other.content.replace('\n',';').strip()

    
class WaitInput:
    """base class for action consisting in waiting for an incoming request"""
    
class ReceiveMessage(IMAction, WaitInput):
    """receive message action"""

class ReceivePresence(IMAction, WaitInput):
    """receive presence action"""
    
class ReceiveInvitation(IMAction, WaitInput):
    """receive conference invitation action"""
    
class ReceiveQuitForum(IMAction, WaitInput):
    """receive quit forum action"""

class SendOutput: 
    """base class for action consisting in sending an outgoing request"""
    
class SendMessage(IMAction, SendOutput):
    """send message action"""

class SendPresence(IMAction, SendOutput):
    """send presence action"""
    
class SendInvitation(IMAction, SendOutput):
    """send invitation action"""
    
class AcceptInvitation(IMAction, SendOutput):
    """send accept invitation action"""
    
class QuitForum(IMAction, SendOutput):
    """send quit forum action"""

class Context(DialogAction):
    """this class is a particular action designed to hold contextual information,
    such as :
    - are we in a regular chat or in a conference room
    - what's the name of the user/bot in the dialog definition
    """
    def __init__(self, name, user_nick, bot_nick, *more_info):
        self.name = name
        self.user_nick =  user_nick
        self.bot_nick = bot_nick
        self.more_info = more_info
        
    def __repr__(self):
        return '<Context: %s, user=%s, bot=%s>' % (self.name,
                                                   self.user_nick,
                                                   self.bot_nick)

    def in_forum(self):
        """return the forum room if any or None"""
        return self.name == 'forum' and self.more_info[0] or None
    
class DialogTester:
    """the dialog test is responsible to execute a dialog and check if the
    behaviour it defines is actually observed
    """
    
    def __init__(self, adaptor, aliases, verbose=True):
        self.adaptor = adaptor
        self.aliases = aliases
        self.queue = None
        self.verbose = verbose
        
    def run_dialog(self, dlg, report):
        """execute an expected dialog and check its execution
        """
        #FIXME TODO - refactor
        TIMEOUT = 10
        assert self.queue is None
        start_time = time.time()
        skipped_previous = False
        self.queue = Queue.Queue()
        try:
            if self.verbose :
                print colorize_ansi("running %s..."%dlg.title, style='bold')
            # initialize report section
            description = None
            context = None
            table = Table(2, title="results", klass="res_table")
            # do not include description for now -- nico -- FIXME
            # if dlg.description:
            #     description = Paragraph([dlg.description])
            nb_done = 0 #number of action effectively proceeded
            # proceed each action
            for action in dlg.actions:
                nb_done += 1
                if self.verbose :
                    print str(action)
                if isinstance(action, Context):
                    self.adaptor.set_context(action)
                    context = Paragraph([str(action)], klass="context")
                elif isinstance(action, WaitInput):
                    table.append(Span([str(action)], klass="wait"))
                    received = None
                    if not skipped_previous:
                        try:
                            while True:
                                received = self.queue.get(timeout=TIMEOUT)
                                if isinstance(received, ReceivePresence) and \
                                       not isinstance(action, ReceivePresence):
                                    if self.verbose :
                                        print '**** ignoring ReceivedPresence ', received
                                    continue
                                else:
                                    break
                            table.add_text(str(received))
                        except Queue.Empty:
                            if action.optional:
                                if self.verbose :
                                    print '**** ignoring Optional ', action
                                skipped_previous = True
                                continue
                            msg = "No message received after %s seconds" % TIMEOUT
                            table.add_text("Error: %s" % msg)
                            raise AssertionError(msg)
                    else:
                        # reset skipped_previous
                        skipped_previous = False
                    # must call is_equivalent on action and not received
                    # since action is the normal form while received may be an
                    # alias
                    if received and not action.is_equivalent(received, self.aliases):
                        if action.optional:
                            if self.verbose :
                                print '**** ignoring Optional ', action
                            skipped_previous = True
                            continue
                        #table.add_text("Error: got '%s' instead" % received)
                        raise AssertionError('%s != %s' % (received, action))
                elif isinstance(action, SendOutput):
                    table.append(Span([str(action)], klass="send"))
                    table.append(Span([str(action)], klass="send"))
                    self.adaptor.send_action(action)
##                     # wait a second to let the bot the time to process
##                     # the message before we eventually send a second one
##                     time.sleep(1)
                else:
                    raise RuntimeError('duh ? %r' % action)
        finally:
            # build up report
            if description:
                report.append(description)
            if context:
                report.append(context)
            report.append(table)
            report.append(Paragraph(["%d actions done in %d sec" %
                                     (nb_done, time.time() - start_time)]))
            # reset queue (ensure each run owns its own Queue
            self.queue = None
        
    def receive_action(self, action):
        """resume the blocked dialog when an action is received"""
        self.queue.put(action)


