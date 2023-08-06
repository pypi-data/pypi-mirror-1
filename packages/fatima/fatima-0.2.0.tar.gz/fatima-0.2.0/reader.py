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
"""classes to create dialog objects from a file (currently only a ReST reader
is available), plus another basic aliases file reader
"""

__revision__ = '$Id: reader.py,v 1.9 2005-06-24 10:03:45 nico Exp $'

import new

from logilab.common.textutils import get_csv

from fatima.dialog import Dialog        


def exception_str(ex):
    """function used to replace default __str__ method of exception instances"""
    return 'on line %s (%r)::\n %s' % (ex.lineno, ex.line,
                                         ', '.join(ex.args))

def complete_exception(ex, lineno, line):
    """complete an exception instance by adding it the line and line number
    describing the place where the parsing failed. More over replace instance's
    __str__ method to include those informations when printed
    """
    ex.line = line
    ex.lineno = lineno
    ex.__str__ = new.instancemethod(exception_str, ex)
    
class Reader:
    """abstract reader, children classes has to implement the from_string
    method to benefit from the from_file generic implementation
    """

    def __init__(self):
        pass
    
    def from_file(self, fpath):
        """open the file and give its content to from_string, returning
        whatever is returned by it
        """
        return self.from_string(open(fpath).read())

    def from_stream(self, stream) :
        """read data from file object then process it
        """
        return self.from_string(stream.read())
        
    def from_string(self, string):
        """override this one !"""
        raise NotImplementedError()

    
class ReSTDialogReader(Reader):
    """class to read dialogs formatted using a ReST compatible format"""
    
    def from_string(self, string):
        """return an iterator on dialog objects, read from a string"""
        for lineno, level, sect_title, sect_content in self.extract_sections(string):
            yield (level, self.dialog_from_section(sect_title, sect_content, lineno))
        
    def extract_sections(self, string):
        """extract interesting sections from a ReST document, return an
        iterator on 4-uples (start line, level, title, content)
        """
        last = None
        section_start = 0
        cur_title = None
        cur_content = []
        cur_level = 0
        for lineno, line in enumerate(string.splitlines()):
            try:
                # title ?
                if line.startswith('==') \
                       or line.startswith('--') or line.startswith('~~'):
                    # if previous section is finished
                    if cur_title:
                        cur_content = '\n'.join(cur_content[:-1]).strip()
                        #if cur_content:
                        yield section_start, cur_level, cur_title, cur_content
                        cur_title = None
                        cur_content = None
                    # get ready for new section
                    section_start = lineno + 1
                    cur_title = last
                    cur_content = []
                    if line.startswith('**') :
                        cur_level = 0
                    elif line.startswith('==') :
                        cur_level = 1
                    elif line.startswith('--') :
                        cur_level = 2
                    elif line.startswith('~~') :
                        cur_level = 3
                # content ?
                elif cur_title:
                    cur_content.append(line)
                last = line
            except Exception, ex:
                complete_exception(ex, lineno, line)
                raise
        # is end of document closing a section ?
        cur_content = '\n'.join(cur_content).strip()
        if cur_title:
            yield section_start, cur_level, cur_title, cur_content

    def dialog_from_section(self, sect_title, sect_content, base_lineno=0):
        """return a Dialog instance created according to a ReST section"""
        dlg = Dialog(sect_title)
        buff, indent = [], None
        base_lineno += len(sect_title.splitlines()) + 1
        for lineno, line in enumerate(sect_content.splitlines()):
            try:
                _line = line.strip()
                if _line == 'Test ::':
                    dlg.description = '\n'.join(buff)
                    buff = []
                elif dlg.description is None:
                    buff.append(line)
                elif _line:
                    # description has been set
                    if not dlg.actions:
                        # this is the first dialog entry, get indent string
                        indent = indent_string(line)
                        dlg.action_string(_line)
                    elif line.startswith(indent):
                        if line[len(indent)].isspace():
                            # this line is the suite of the previous action
                            dlg.actions[-1].add_content(line)
                        else:
                            # new action
                            dlg.action_string(_line)
                    else:
                        # line doesn't start with the indent string
                        # -> end of this dialog, ignore the rest of the sect
                        break
            except Exception, ex:
                complete_exception(ex, lineno + base_lineno, line)
                raise
        return dlg


def indent_string(line):
    """return the part of the line used as indentation (i.e. spaces
    characters at the beginning of the line)
    """
    res = []
    for char in line:
        if char.isspace():
            res.append(char)
        else:
            break
    return ''.join(res)


class AliasesReader(Reader):
    """read aliases (i.e. an alias is a mapping from a word or sentence
    to its equivalent words / sentences), where aliases definition has
    the following syntax ::

      # comments are lines starting with a # (only full line supported)

      # an alias definition must begin at the first character of a line
      # then "=" is separating the normal form from its aliases, and aliases
      # are separated using a comma
      normalized form = derived form 1, derived form 2, and another one
      
      # then you can add more form on following lines by starting the line
      # with at least one space or tab character
        more derived form, ...

      new alias = bla, bidibou, and so on
    """
      
    def from_string(self, string):
        """return a dictionary of aliases readen from a string"""
        result = {}
        norm_word = None
        for line in string.splitlines():
            if not line.strip() or line.strip().startswith('#'):
                continue
            if not line[0].isspace():
                norm_word, aliases = line.split('=', 1)
                norm_word = norm_word.strip()
                assert norm_word not in result, (norm_word, result)
                result[norm_word] = [norm_word] + get_csv(aliases)
            else:
                result[norm_word] += get_csv(line)
        return result
