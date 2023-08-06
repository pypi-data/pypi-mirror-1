#!/usr/bin/env python
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
"""imtestcli [OPTIONS] <dialogfile>

This script connect to an instant messaging (im) server and test an
expected dialog with (usually) a bot. For now only the Jabber protocol is
handled but this software has been written to be easily extendable to other
protocol such as msn, aim, irc...
"""

__revision__ = '$Id: imtestcli.py,v 1.21 2005-06-24 10:03:44 nico Exp $'

import sys
import time
from getpass import getpass

from logilab.common.configuration import Configuration
from logilab.common.ureports import build_summary
from logilab.common.ureports.nodes import Section, Span, Paragraph
from logilab.common.ureports.html_writer import HTMLWriter
from logilab.common.ureports.text_writer import TextWriter
from logilab.common.ureports.docbook_writer import DocbookWriter
from logilab.common.textutils import colorize_ansi

from fatima.jabber import JabberAdapter, TwistedJabberClient
from fatima.dialog import DialogTester
from fatima.reader import ReSTDialogReader, AliasesReader

from mx.DateTime import now

class MyHTMLWriter(HTMLWriter):
    """HTML writer that knows about stylesheets"""

    def begin_format(self, layout):
        """begin to format a layout"""
        self.section = 0
        self.writeln('<html>')
        self.writeln('<head>')
        self.writeln('<link rel="stylesheet" type="text/css" href="default.css"/>')
        self.writeln('<title>fatima report</title>')
        self.writeln('</head>')
        self.writeln('<body>')

    def end_format(self, layout):
        """finished to format a layout"""
        self.writeln('Generated on %s by fatima' % now())
        if self.snipet is None:
            self.writeln('</body>')
            self.writeln('</html>')


CFG = None

def get_writer(format):
    """return a ureport writter according to the desired format"""
    format = format.lower().strip()
    if format == 'html':
        return MyHTMLWriter()
    elif format == 'docbook':
        return DocbookWriter()
    elif format == 'rest':
        return TextWriter()
    raise Exception('Unknown format %r' % format)

class FatimaRunner :
    """
    run tests for a given config
    """

    def __init__(self, title, test_file, cfg, verbose=True) :
        """
        result title, stream from which to read tests, config to use
        """
        self.verbose = verbose
        
        # aliases
        if cfg['aliases-file']:
            aliases = AliasesReader().from_file(cfg['aliases-file'])
        else:
            aliases = {}

        # password
        password = cfg['password'] or getpass('password: ')

        # adapter, client, tester are bound together
        adapter = JabberAdapter(debug=cfg['debug'])
        self.client = TwistedJabberClient(adapter, cfg['server'],
                                          cfg['user'], password,
                                          debug=cfg['debug'], verbose=verbose)
        self.tester = DialogTester(adapter, aliases, verbose=verbose)
        adapter.client = self.client
        adapter.tester = self.tester

        # what tests should run ?
        if cfg['match']:
            self._should_run = cfg['match'].match
        else:
            self._should_run = lambda x: 1

        # where to write report ?
        self.writer = get_writer(cfg['format'])
        self.format = cfg['format']
        self.document = Section(id="main", title="Test Report for %s" % title)

        # read tests
        reader = ReSTDialogReader()
        self._tests = reader.from_stream(test_file)

    def run(self, output=None) :
        """
        run tests read from input stream and write report to output
        by default output is sys.stdout (set in writer)
        """
        # connect to the jabber server
        self.client.connect()
        #time.sleep(3) # FIXME: wait for connexion establishement ? reactivate

        # local vars
        succeed = []
        failed = []
        not_tested = []
        cur_level = 0
        sections = []
        try:
            # process each dialog
            test_sect = Section(id="test", title="Tests details")
            sections.append(test_sect)
            for level, dlg in list(self._tests):
                test_details_sect = Section(title=dlg.title, id=dlg.title.replace(' ', '_'))

                # handle multi-level of sections
                #print [s.children[0].children[0].data for s in sections], cur_level,'--',level, dlg.title
                if level <= cur_level :
                    sections = sections[:level]
                sections[-1].append(test_details_sect)
                sections.append(test_details_sect)
                cur_level = level

                if not dlg.actions or not self._should_run(dlg.title):
                    # do not include description for now -- nico -- FIXME
                    #if dlg.description:
                    #    test_details_sect.append(Paragraph([dlg.description]))
                    if dlg.actions :
                        test_details_sect.append(Paragraph(['This test was not run.']))
                        if self.verbose :
                            print colorize_ansi('[%s - IGNORED]' % dlg.title, 'yellow')
                        not_tested.append(dlg.title)
                    #else:
                    #    test_details_sect.append(Paragraph(['No test defined.']))
                    continue
                try:
                    self.tester.run_dialog(dlg, test_details_sect)
                except AssertionError, ex:
                    test_details_sect.children[0].append(Span([' [FAILED]'], klass="error"))
                    if self.verbose :
                        print colorize_ansi('[%s - FAILED - %s]' % (dlg.title, ex), 'red')
                    failed.append(dlg.title)
                else:
                    test_details_sect.children[0].append(Span([' [SUCCEED]'], klass="success"))
                    if self.verbose :
                        print colorize_ansi('[%s - SUCCEED]' % dlg.title, 'green')
                    succeed.append(dlg.title)
            # general results
            general_results_sect = Section(id="sumup", title="General results")
            if len(failed) + len(succeed):
                sreport = '''Total of %s tests. %s succeed, %s failed (%s%% failure), %s ignored (%s%% ignored).''' % (
                    len(failed) + len(succeed) + len(not_tested),
                    len(succeed), len(failed), 
                    len(failed) * 100 / (len(failed) + len(succeed)),
                    len(not_tested),
                    len(not_tested) * 100 / (len(failed) + len(succeed) + len(not_tested)))
            else:
                sreport = 'nothing tested.'
            if self.verbose :
                print colorize_ansi(sreport, style='bold')
            general_results_sect.append(Paragraph([sreport]))
            self.document.append(general_results_sect)
            self.document.append(test_sect)
            if self.format == 'html' :
                self.document.insert(1, build_summary(self.document, 4))
            elif self.format == 'rest' :
                self.document.insert(1, Paragraph(['.. contents::']))
        finally:
            self.client.stop()
            self.writer.format(self.document, output)
            # avoid exception while twisted is shutting down
            #time.sleep(2) FIXME reactivate

    
def usage(status=0):
    """display program usage and exit"""
    print CFG.help()
    sys.exit(status)

def cb_generate_config(*args, **kwargs):
    """generate a sample configuration and exit"""
    CFG.generate_config()
    sys.exit(0)
    
def cb_load_config(option, opt_name, opt_value, parser):
    """generate a sample configuration and exit"""
    CFG.load_file_configuration(opt_value)

OPTIONS = [
    ('server',
     {'type':'string',
      'metavar': '<host[:port]>', 'short': 's',
      'help': 'im server host and (optionaly) port, preceded by a colon (":")',
      'default': 'jabber.logilab.org'}),
    
    ('user',
     {'type': 'string',
      'metavar': '<userid>', 'short': 'u',
      'help': 'identifier to use to connect to the im server. It should be the \
same as the one used in the dialog definition '}),
    
    ('password',
     {'type': 'string',
      'metavar': '<password>', 'short': 'p',
      'help': 'password to use to connect to the im server. If not given using \
this option, you will be prompted for it'}),

##     ('bot',
##      {'type': 'string',
##       'metavar': '<botid>', 'short': 'b',
##       'help': 'identifier of the bot to test'}),

    ('match',
     {'type': 'regexp',
      'metavar': '<regexp>', 'short': 'm',
      'help': 'run only tests which have a title matching this regular \
expression'}),

    ('config',
     {'action': 'callback', 'callback': cb_load_config, 'type': 'string',
      'metavar': '<configfile>', 'short': 'c',
      'help': 'path to a configuration file'}),
    
    ('debug',
     {'type': 'yn',
      'metavar': '<y or n>', 'short': 'd',
      'help': 'run in debug mode, providing more information about what\'s \
happen'}),
    
    ('output',
     {'type': 'string',
      'metavar': '<filepath>', 'short': 'o',
      'help': "Set file where to write result"}),
    
    ('format',
     {'type': 'string',
      'metavar': '<format>', 'short': 'f',
      'help': "Set Format output within (rest, html, docbook). [rest] by default",
      'default': 'rest'}),

    ('aliases-file',
     {'type': 'string',
      'metavar': '<filepath>', 'short': 'a',
      'help' : '''read aliases from the given file'''}),
    
    ('generate-rcfile',
     {'action' : 'callback', 'callback' : cb_generate_config,
      'help' : '''generate a sample configuration file according to \
the current configuration. You can put other options before this one to use \
them in the configuration. This option causes the program to exit'''}),
    ]

def run(args=None):
    """main function"""

    # manage args
    if args is None:
        args = sys.argv[1:]
    global CFG
    CFG = Configuration(options=OPTIONS, name='IM TEST',
                        usage=__doc__, doc="FATIMA's configuration file")
    args = CFG.load_command_line_configuration(args)
    if len(args) != 1:
        usage(1)

    if CFG['output']:
        output = file(CFG['output'], 'w')
    else:
        output = sys.stdout

    # go
    runner = FatimaRunner(args[0], file(args[0]), CFG)
    runner.run(output)
    
if __name__ == '__main__':
    run()
