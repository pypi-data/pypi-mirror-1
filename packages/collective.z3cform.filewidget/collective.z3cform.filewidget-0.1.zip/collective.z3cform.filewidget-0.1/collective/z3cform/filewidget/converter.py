from zope.component import adapts
from zope.schema.interfaces import IBytes
from z3c.form.converter import FileUploadDataConverter as BaseFileUploadDataConverter
from collective.z3cform.filewidget.interfaces import IFileWidget, NOCHANGE

import cgi
import zope.publisher.browser
import ZPublisher.HTTPRequest


class FileUploadDataConverter(BaseFileUploadDataConverter):
    """A special data converter for bytes, supporting also FileUpload.

    Since IBytes represents a file upload too, this converter can handle
    zope.publisher.browser.FileUpload object as given value.
    """
    adapts(IBytes, IFileWidget)

    def toWidgetValue(self, value):
        return value

    def toFieldValue(self, value):
        """See interfaces.IDataConverter"""
        if value == NOCHANGE:
            return value
            
        if isinstance(value, ZPublisher.HTTPRequest.FileUpload):
            fieldstorage = cgi.FieldStorage()
            fieldstorage.file = value
            fieldstorage.headers = value.headers
            fieldstorage.filename = value.filename
            value = zope.publisher.browser.FileUpload(fieldstorage)
        return super(FileUploadDataConverter, self).toFieldValue(value)

