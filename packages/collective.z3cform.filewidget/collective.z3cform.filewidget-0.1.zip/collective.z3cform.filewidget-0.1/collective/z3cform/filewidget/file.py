##############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""T Widget Implementation

$Id: file.py 78513 2007-07-31 23:03:47Z srichter $
"""
__docformat__ = "reStructuredText"
import zope.component
import zope.interface
import zope.schema.interfaces
import ZPublisher.HTTPRequest

from z3c.form import  widget, interfaces
from z3c.form.browser import text
from collective.z3cform.filewidget.interfaces import IFileWidget, NOCHANGE

class FileWidget(text.TextWidget):
    """Input type text widget implementation."""
    zope.interface.implementsOnly(IFileWidget)

    klass = u'file-widget'

    # Filename and headers attribute get set by ``IDataConverter`` to the widget
    # provided by the FileUpload object of the form.
    headers = None
    filename = None
        
    def exists(self):
        if not self.value:
            return False

        if self.request.has_key(self.name) and \
            isinstance(self.request.get(self.name), ZPublisher.HTTPRequest.FileUpload):
            # We have the real file in request => we cannot pass it back so behave like it's not there
            return False
            
        return True
            
    def getFilename(self):
        # Tries to retrieve the filename
        if hasattr(self.value, 'filename'):
            return getattr(self.value,'filename')
        elif self.request.has_key('%s.filename' % self.name):
            return self.request.get('%s.filename' % self.name)
        else:
            return self.filename
            
    
    def extract(self, default=interfaces.NOVALUE):
        """See z3c.form.interfaces.IWidget."""
        if self.request.get("%s.nochange" % self.name,'') == "nochange":
            return NOCHANGE
            
        return self.request.get(self.name, default)


@zope.component.adapter(zope.schema.interfaces.IBytes, interfaces.IFormLayer)
@zope.interface.implementer(interfaces.IFieldWidget)
def FileFieldWidget(field, request):
    """IFieldWidget factory for FileWidget."""
    return widget.FieldWidget(field, FileWidget(request))
