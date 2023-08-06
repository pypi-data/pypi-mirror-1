# -*- coding: utf-8 -*-

import grokcore.component as grok
from dolmen.file import IFileField
from dolmen.widget.file import IFileWidget
from z3c.form.interfaces import NOT_CHANGED, IDataConverter


class UploadToNamedFile(grok.MultiAdapter):
    """Returns a FileUpload object, as it has been uploaded.
    """
    grok.implements(IDataConverter)
    grok.adapts(IFileField, IFileWidget)

    def __init__(self, field, widget):
        self.field = field
        self.widget = widget

    def toWidgetValue(self, value):
        return value

    def toFieldValue(self, value):
        if value is None or value == '':
            return NOT_CHANGED
        return value
