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

from z3c.form.browser.textarea import TextAreaWidget
from z3c.form.interfaces import IFormLayer, IFieldWidget
from z3c.form.widget import FieldWidget

from zw.schema.richtext.interfaces import IRichText
from zw.widget.tiny.interfaces import ITinyWidget

try:
    from zc import resourcelibrary
    haveResourceLibrary = True
except ImportError:
    haveResourceLibrary = False

OPT_PREFIX = "mce_"
OPT_PREFIX_LEN = len(OPT_PREFIX)
MCE_LANGS=[]
import glob
import os

# initialize the language files
for langFile in glob.glob(
    os.path.join(os.path.dirname(__file__), 'tiny_mace', 'langs') + '/??.js'):
    MCE_LANGS.append(os.path.basename(langFile)[:2])

class TinyWidget(TextAreaWidget):
    """TinyMCE widget implementation.
    """
    implementsOnly(ITinyWidget)

    klass = u'tiny-widget'
    value = u''

    tiny_js = u""

    rows = 10
    cols = 60

    mce_theme = "advanced"
    mce_theme_advanced_buttons1 = "bold,italic,underline,separator,strikethrough,justifyleft,justifycenter,justifyright, justifyfull,bullist,numlist,undo,redo,link,unlink"
    mce_theme_advanced_buttons2 = ""
    mce_theme_advanced_buttons3 = ""
    mce_theme_advanced_toolbar_location = "top"
    mce_theme_advanced_toolbar_align = "left"
    mce_theme_advanced_statusbar_location = "bottom"
    mce_extended_valid_elements = "a[name|href|target|title|onclick],img[class|src|border=0|alt|title|hspace|vspace|width|height|align|onmouseover|onmouseout|name],hr[class|width|size|noshade],font[face|size|color|style],span[class|align|style]"

    def update(self):
        super(TinyWidget, self).update()


        if haveResourceLibrary:
            resourcelibrary.need('tiny_mce')

        mceOptions = []
        for k in dir(self):
            if k.startswith(OPT_PREFIX):
                v = getattr(self, k, None)
                v = v==True and 'true' or v==False and 'false' or v
                if v in ['true','false']:
                    mceOptions.append('%s : %s' % (k[OPT_PREFIX_LEN:],v))
                elif v is not None:
                    mceOptions.append('%s : "%s"' % (k[OPT_PREFIX_LEN:],v))
        mceOptions = ', '.join(mceOptions)
        if mceOptions:
            mceOptions += ', '
        if self.request.locale.id.language in MCE_LANGS:
            mceOptions += ('language : "%s", ' % \
                               self.request.locale.id.language)
            
        self.tiny_js = u"""
tinyMCE.init({ 
mode : "exact", %(options)s
elements : "%(id)s"
}
);
""" % { "id": self.id,
        "options": mceOptions }



@adapter(IRichText, IFormLayer)
@implementer(IFieldWidget)
def TinyFieldWidget(field, request):
    """IFieldWidget factory for TinyWidget.
    """
    return FieldWidget(field, TinyWidget(request))
