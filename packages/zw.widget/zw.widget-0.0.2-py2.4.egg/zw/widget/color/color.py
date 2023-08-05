#-*- coding: utf-8 -*-
#############################################################################
#                                                                           #
#   Copyright (c) 2007-2008 Gregor Giesen <vogon@zaehlwerk.net>             #
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

from zw.vogon.i18n import MessageFactory as _

from zope.component import adapter, adapts
from zope.interface import implementsOnly, implementer

from z3c.form.browser import widget
from z3c.form.converter import BaseDataConverter
from z3c.form.interfaces import IField, IFieldWidget, IWidget, IFormLayer
from z3c.form.widget import Widget, FieldWidget

from zw.schema.color.interfaces import IColor
from zw.widget.color.interfaces import IColorWidget

class ColorWidget(widget.HTMLTextInputWidget, Widget):
    """Lines widget.
    """
    implementsOnly(IColorWidget)
    
    klass = u'color-widget'
    value = u''

    def update(self):
        super(ColorWidget, self).update()
        widget.addFieldClass(self)

@adapter(IColor, IFormLayer)
@implementer(IFieldWidget)
def ColorFieldWidget(field, request):
    """IFieldWidget factory for ColorWidget.
    """
    return FieldWidget(field, ColorWidget(request))

