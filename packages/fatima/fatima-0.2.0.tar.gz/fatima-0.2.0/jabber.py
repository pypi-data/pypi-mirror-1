# pylint: disable-msg=C0101
#
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
"""jabber plugin for the im test bot"""

__revision__ = '$Id: jabber.py,v 1.8 2005-06-24 10:03:45 nico Exp $'

import sys
from threading import Thread

from twisted.protocols import xmlstream
from twisted.protocols.jabber import client, jid
from twisted.xish import domish
from twisted.internet import reactor

from fatima.dialog import ReceiveMessage, ReceivePresence, \
     ReceiveInvitation, ReceiveQuitForum

JABBER_CLIENT_NS = 'jabber:client'
    
class TwistedJabberClient:

    def __init__(self, dlghdlr, server, userid, userpwd,
                 autoregister=False, debug=False, verbose=True):
        # dialog handler
        self.dlghdlr = dlghdlr
        # jabber connexion information
        self.server = server
        try:
            self.host, self.port = server.split(':')
        except ValueError:
            self.host = server
            self.port = 5222
        else:
            self.port = int(self.port)
        self.userid = userid
        self.userpwd = userpwd
        self.autoregister = autoregister
        self.debug = debug
        self._fact = None
        self._send = None
        self._waiting_roster = None
        self.verbose = verbose
        
    def jid_string(self, user, conf=None, resource=True):
        """make and return a Jabber identifier (jid) for a user's nick.

        if conf is a non empty string, use this string as the conference room
        and go through the conferences server

        if resource is true, append the 'imtest' resource to the jid
        """
        if conf:
            if resource:
                return "%s@conference.%s/%s" % (conf, self.server, user)
            return "%s@conference.%s" % (conf, self.server)
        if resource:
            return "%s@%s/imtest" % (user, self.server)
        return "%s@%s" % (user, self.server)
    
    def connect(self):
        """connect to the jabber server"""
        jid_str = self.jid_string(self.userid)
        self._fact = factory = client.basicClientFactory(jid.JID(jid_str),
                                                         self.userpwd)
        factory.addBootstrap(xmlstream.STREAM_AUTHD_EVENT, self.authenticate)
        factory.addBootstrap(client.BasicAuthenticator.INVALID_USER_EVENT,
                             self.invalid_user)
        factory.addBootstrap(client.BasicAuthenticator.AUTH_FAILED_EVENT,
                             self.fatal_error)
        factory.addBootstrap(client.BasicAuthenticator.REGISTER_FAILED_EVENT,
                             self.fatal_error)
        if self.verbose :
            print 'connecting to server %s using id %s...' % (self.server,
                                                              self.userid),
        reactor.connectTCP(self.host, self.port, factory)
        thread = Thread(target=reactor.run, name='twisted main loop',
                        kwargs={'installSignalHandlers': False})
        # added this because the twisted thread never return,
        # even after a call to stop(). Probably i didn't finnd the right
        # way to interact with twisted...
        thread.setDaemon(True)
        thread.start()

    def stop(self):
        """disconnect from the jabber server"""
        reactor.disconnectAll()
        reactor.callFromThread(reactor.stop)#stop()

    def send(self, twxml):
        """send a twisted xml element"""
        if self.debug:
            print '-> sending', twxml.toXml()
        self._send(twxml)
        
    def authenticate(self, twxml):
        """authentication callback"""
        # bind twxml.send to self
        self._send = twxml.send
        # add observer for incoming message / presence requests
        twxml.addObserver("/iq",       self.iq_hdlr)
        twxml.addObserver("/presence", self.dlghdlr.presence_hdlr)
        twxml.addObserver("/message",  self.dlghdlr.message_hdlr)
        if self.verbose :
            print 'connected'
        # FIXME: need to request the roster ?
        # request roster
        self._waiting_roster = True
        iq = domish.Element((JABBER_CLIENT_NS, 'iq'))
        iq['type'] = 'get'
        iq.addElement(('jabber:iq:roster', 'query'))
        self.send(iq)

    def invalid_user(self, twxml):
        """invalid user callback"""
        # should we try to register a new account to the server ?
        if self.autoregister:
            print 'registering user %s to the jabber server' % self.userid
            self._fact.authenticator.registerAccount(self.userid, self.userpwd)
        else:
            self.fatal_error(twxml)

    def fatal_error(self, twxml):
        """unrecoverable error callback"""
        print 'unrecoverable error:'
        print twxml.toXml()
        self.stop()

    def iq_hdlr(self, twxml):
        """handle a iq packet

        :type twxml: `twisted.xish.domish.Element`
        :param twxml: the xml stream containing a iq element
        """
        if self._waiting_roster and twxml.query.uri == 'jabber:iq:roster':
            # got roster, send presence so clients know we're actually online
            presence = domish.Element((JABBER_CLIENT_NS, 'presence'))
            presence.addElement('status').addContent('Online')
            self.send(presence)
            self._waiting_roster = False


class JabberAdapter:
    """adapt action for the jabber client"""

    def __init__(self, debug=False, verbose=True):
        self.debug = debug
        self.verbose = verbose
        self.context = None # is set dynamically during dialog execution
        self.client = None # will be set later due to a cyclic dependency
        self.tester = None # will be set later due to a cyclic dependency

    def set_context(self, context):
        """change the current dialog's context"""
        self.context = context

    def check_from(self, from_jid):
        """check if request from user with the given jabber id should be
        considered, return the nick extracted from the jabber id, else
        return None
        """
        if self.context is None:
            print '*** dropping request from %s, no context set' % from_jid
            return
        # drop requests from other people than the bot since
        # we usually use an actual account with friends registered in roster
        sender = from_jid.split('@')[0]
        if sender == self.context.bot_nick or sender == self.context.in_forum():
            return sender
        if self.verbose :
            print '*** dropping request from', from_jid
        return
    
    def send_action(self, action):
        """convert the action into twisted xml and give it back to the
        jabber client
        """
        self.client.send(self.action2twxml(action))

    def presence_hdlr(self, twxml):
        """jabber client hook: handle a presence packet, transform it
        into the right action and give it back to the dialog tester

        :type twxml: `twisted.xish.domish.Element`
        :param twxml: the xml stream containing a presence element
        """
        sender = self.check_from(twxml['from'])
        action = None
        if self.debug:
            print '-< received', twxml.toXml()
        if sender:
            if sender == self.context.in_forum():
                from_user = twxml['from'].split('/', 1)[1]
                
                if from_user != self.context.user_nick:
                    if twxml.getAttribute('type') == 'unavailable':
                        action = ReceiveQuitForum(from_user, sender)
                    else:
                        action = ReceivePresence(from_user, sender)
            else:
                action = ReceivePresence(sender, twxml['to'])
        if action is not None:
            self.tester.receive_action(action)
        
    def message_hdlr(self, twxml):
        """jabber client hook: handle a message packet, transform it
        into the right action and give it back to the dialog tester

        :type twxml: `twisted.xish.domish.Element`
        :param twxml: the xml stream containing a message element
        """
        # ignore delayed / error messages
        for elmt in twxml.elements():
            if elmt.uri == 'jabber:x:delay' or \
                   elmt.getAttribute('type') == 'error':
                if self.debug:
                    print '*** dropped delayed msg', twxml.toXml()
                return
        from_jid = twxml['from']
        if self.debug:
            print '-< received', twxml.toXml()
        sender = self.check_from(from_jid)
        if sender:
            in_forum = self.context.in_forum()
            if in_forum:
                # drop messages from conference room (i.e. no resource set)
                try:
                    quser, resource = from_jid.split('/', 1)
                except ValueError:
                    if self.verbose :
                        print '*** dropping message from %s (no resource set)' % from_jid
                    return
            for elmt in twxml.elements():
                # invited in a group chat ?
                if elmt.uri == 'jabber:x:conference':
                    action = ReceiveInvitation(sender, elmt['jid'].split('@')[0])
                    break
            else:
                if sender == in_forum:
                    sender = twxml['from'].split('/', 1)[1]
                    if sender == self.context.user_nick:
                        if self.verbose :
                            print '*** ignoring message from myself...'
                        return
                action = ReceiveMessage(sender, str(twxml.body))
            self.tester.receive_action(action)

    def action2twxml(self, action):
        """transform an action into a twisted xml element"""
        meth_name = '%s2twxml' % action.__class__.__name__.lower()
        return getattr(self, meth_name)(action)

    def sendmessage2twxml(self, action):
        """transform a SendMessage action into a twisted xml element"""
        in_forum = self.context.in_forum()
        twxml = domish.Element((JABBER_CLIENT_NS, 'message'))
        twxml['type'] = in_forum and 'groupchat' or 'chat'
        twxml['to'] = self.client.jid_string(self.context.bot_nick, in_forum, resource=False)
        twxml['from'] = self.client.jid_string(self.context.user_nick,
                                               in_forum)
        body = domish.Element((JABBER_CLIENT_NS, 'body'))
        body.addChild(action.content)
        twxml.addChild(body)
        return twxml

    def sendpresence2twxml(self, action):
        """transform a SendPresence action into a twisted xml element"""
        in_forum = self.context.in_forum()
        if in_forum:
            to = self.client.jid_string(self.context.user_nick, in_forum)
        else:
            to = self.client.jid_string(self.context.bot_nick, resource=False)
        return presence_elmt(self.client.jid_string(self.context.user_nick), to)
    
    def sendinvitation2twxml(self, action):
        """transform a SendPresence action into a twisted xml element"""
        forum = action.content
        assert forum
        twxml = domish.Element((JABBER_CLIENT_NS, 'message'))
        twxml['type'] = 'normal'
        twxml['to'] = self.client.jid_string(self.context.bot_nick,
                                             resource=False)
        twxml['from'] = self.client.jid_string(self.context.user_nick)
        body = domish.Element((JABBER_CLIENT_NS, 'body'))
        body.addChild('You are invited to %s by %s' % (forum,
                                                       self.context.user_nick))
        twxml.addChild(body)
        x = domish.Element((JABBER_CLIENT_NS, 'x'))
        x['jid'] = forum
        x['xmlns'] = 'jabber:x:conference'
        twxml.addChild(x)
        return twxml
    
    def acceptinvitation2twxml(self, action):
        """transform a SendPresence action into a twisted xml element"""
        forum = self.client.jid_string(self.context.user_nick, action.content)
        return presence_elmt(self.client.jid_string(self.context.user_nick),
                             forum)

    def quitforum2twxml(self, action):
        """transform a SendPresence action into a twisted xml element"""
        forum = self.client.jid_string(self.context.user_nick, action.content)
        return presence_elmt(self.client.jid_string(self.context.user_nick),
                             forum, 'unavailable')



def presence_elmt(from_, to, p_type=None):
    """create and return a xml presence element"""
    twxml = domish.Element((JABBER_CLIENT_NS, 'presence'))
    twxml['from'] = from_
    twxml['to'] = to
    if p_type:
        twxml['type'] = p_type
    return twxml
    
