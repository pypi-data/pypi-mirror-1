# -*- coding: UTF-8 -*-
# Copyright (C) 2005 Luis Arturo Belmar-Letelier <luis@itaapy.com>
# Copyright (C) 2005-2008 Juan David Ibáñez Palomar <jdavid@itaapy.com>
# Copyright (C) 2008 Matthieu France <matthieu@itaapy.com>
# Copyright (C) 2008 Sylvain Taverne <sylvain@itaapy.com>
# Copyright (C) 2008 Wynand Winterbach <wynand.winterbach@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# Import from the Standard Library
from compiler import parse, walk

# Import from itools
from text import TextFile
from registry import register_handler_class

class VisitorUnicode(object):

    def __init__(self):
        self.messages = []


    def visitConst(self, const):
        from itools.srx import TEXT
        if type(const.value) is unicode and const.value.strip():
            # Context = None
            msg = ((TEXT, const.value),), None, const.lineno
            self.messages.append(msg)



class Python(TextFile):

    class_mimetypes = ['text/x-python']
    class_extension = 'py'


    def get_units(self, srx_handler=None):
        data = self.to_str()
        # Make it work with Windows files (the parser expects '\n' ending
        # lines)
        data = ''.join([ x + '\n' for x in data.splitlines() ])
        # Parse and Walk
        ast = parse(data)
        visitor = VisitorUnicode()
        walk(ast, visitor)

        return visitor.messages


register_handler_class(Python)
