# -*- coding: utf-8 -*-

import grokcore.view as grok
import megrok.z3cform.base as z3cform

from zope.size import byteDisplay
from zope.interface import Interface, implements
from zope.component import getMultiAdapter
from zope.traversing.browser.absoluteurl import absoluteURL
from zope.cachedescriptors.property import CachedProperty

from z3c.form.browser import file
from dolmen.file import INamedFile, IFileField


class IFileWidget(Interface):
    """A widget that represents a file.
    """


class FileWidget(file.FileWidget):
    """A widget for a named file object
    """
    klass = u'file-widget'
    value = None
    implements(IFileWidget)

    def update(self):
        file.FileWidget.update(self)
        try:
            self.url = absoluteURL(self.context, self.request)
        except TypeError:
            self.url = None
        
    @property
    def allow_nochange(self):
        return not self.ignoreContext and \
                   self.field is not None and \
                   self.value is not None and \
                   self.value != self.field.missing_value

    @CachedProperty
    def filename(self):           
        if INamedFile.providedBy(self.value):
            return self.value.filename
        return None
 
    @CachedProperty
    def file_size(self):
        if INamedFile.providedBy(self.value):
            size = self.value.getSize()
            return {'raw': size, 'display': byteDisplay(size)}
        return None

    @CachedProperty
    def download_url(self):
        if self.field is None or self.ignoreContext or not self.url:
            return None
        return '%s/++download++%s' % (self.url, self.field.__name__)

    def extract(self, default=z3cform.NOVALUE):
        """Looks at the selected option to decide which action
        is to be executed : nothing, replace, delete.
        """
        nochange = self.request.get("%s.nochange" % self.name, None)
 
        if nochange == 'nochange':
            dm = getMultiAdapter(
                (self.context, self.field), z3cform.IDataManager)
            return dm.get()
        elif nochange == 'delete':
            return default
        else:
            return file.FileWidget.extract(self, default)


class FileWidgetInput(z3cform.WidgetTemplate):
    grok.context(Interface)
    grok.layer(z3cform.IFormLayer)
    grok.template('templates/input.pt')
    z3cform.directives.field(IFileField)
    z3cform.directives.widget(IFileWidget)
    z3cform.directives.mode(z3cform.INPUT_MODE)


class FileWidgetDisplay(z3cform.WidgetTemplate):
    grok.context(Interface)
    grok.layer(z3cform.IFormLayer)
    grok.template('templates/display.pt')
    z3cform.directives.field(IFileField)
    z3cform.directives.widget(IFileWidget)
    z3cform.directives.mode(z3cform.DISPLAY_MODE)


@grok.adapter(IFileField, z3cform.IFormLayer)
@grok.implementer(z3cform.IFieldWidget)
def FileFieldWidget(field, request):
    """IFieldWidget factory for FileWidget."""
    return z3cform.FieldWidget(field, FileWidget(request))
