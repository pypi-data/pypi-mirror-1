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

import zope.schema.interfaces
from zope.component import adapter
from zope.interface import implementsOnly, implementer

from z3c.form.browser.widget import HTMLTextAreaWidget, addFieldClass
from z3c.form.interfaces import IFormLayer, IFieldWidget
from z3c.form.widget import Widget, FieldWidget

from zw.widget.lines.interfaces import ILinesWidget

class LinesWidget(HTMLTextAreaWidget, Widget):
    """Lines widget.
    """
    implementsOnly(ILinesWidget)
    
    klass = u'lines-widget'
    value = u''

    def update(self):
        super(LinesWidget, self).update()
        addFieldClass(self)
        
@adapter(zope.schema.interfaces.IList, IFormLayer)
@implementer(IFieldWidget)
def LinesFieldWidget(field, request):
    """IFieldWidget factory for LinesWidget.
    """
    return FieldWidget(field, LinesWidget(request))
