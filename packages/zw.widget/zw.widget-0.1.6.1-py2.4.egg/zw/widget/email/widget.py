#-*- coding: utf-8 -*-
#############################################################################
#                                                                           #
#   Copyright (c) 2008 Gregor Giesen <giesen@zaehlwerk.net>                 #
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

from zope.component import adapter, adapts
from zope.interface import implementsOnly, implementer
from zope.app.security.interfaces import IUnauthenticatedPrincipal

from z3c.form.browser import widget
from z3c.form.interfaces import IFieldWidget, IFormLayer
from z3c.form.widget import Widget, FieldWidget

from z3c.schema.email.interfaces import IRFC822MailAddress
from zw.widget.email.interfaces import IEmailWidget

class EmailWidget(widget.HTMLTextInputWidget, Widget):
    """Email widget.
    """
    implementsOnly(IEmailWidget)
    
    klass = u'email-widget'
    value = u''

    obscured = False

    def update(self):
        # Obscure email if unauthenticated.
        self.obscured = IUnauthenticatedPrincipal.providedBy(
            self.request.principal)
        super(EmailWidget, self).update()
        widget.addFieldClass(self)

@adapter(IRFC822MailAddress, IFormLayer)
@implementer(IFieldWidget)
def EmailFieldWidget(field, request):
    """IFieldWidget factory for EmailWidget.
    """
    return FieldWidget(field, EmailWidget(request))

