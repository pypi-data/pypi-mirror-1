#-*- coding: utf-8 -*-
#############################################################################
#                                                                           #
#   Copyright (c) 2007-2008 Gregor Giesen <giesen@zaehlwerk.net>            #
#                                                                           #
# This program is free software; you can redistribute it and/or modify      #
# it under the terms of the GNU General Public License as published by      #
# the Free Software Foundation; either version 3 of the License, or         #
# (at your option) any later version.                                       #
#                                                                           #
# This program is distributed in the hope that it will be useful,           #
# but WITHOUT ANY WARRANTY; without even the implied warranty of            #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the             #
# GNU General Public License for more details.                              #
#                                                                           #
# You should have received a copy of the GNU General Public License         #
# along with this program.  If not, see <http://www.gnu.org/licenses/>.     #
#                                                                           #
#############################################################################
"""
$Id$
"""
__docformat__ = 'reStructuredText'

from zw.widget.i18n import MessageFactory as _

import zope.schema
from z3c.form.interfaces import ITextAreaWidget

class ITinyWidget(ITextAreaWidget):
    """A WYSIWYG input widget for editing html which uses tinymce
    editor.
    """
    
    tiny_js = zope.schema.Text(
        title = u'TinyMCE init ECMAScript code',
        description = u'This ECMAScript code initialize the TinyMCE widget ' \
            u'to the textarea.',
        required = False )
