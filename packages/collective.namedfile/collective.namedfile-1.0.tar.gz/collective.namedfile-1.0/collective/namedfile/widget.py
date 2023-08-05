from zope.app.form.browser.widget import DisplayWidget, renderElement
from zope.app.form.browser.textwidgets import FileWidget, escape
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile

from file import NamedFile

class NamedFileWidget(FileWidget):
    """A correctly working File widget.

    The standard FileWidget returns a string instead of an IFile inst,
    which means it will always fail schema validation in formlib.

    In addition this widget will also extract the filename and Content-Type
    from the request.
    """
    template = ViewPageTemplateFile('inputwidget.pt')
    displayWidth = 30
    
    def __call__(self):
        #
        # This essentially replicates the archetypes file widget functionality
        # XXX TODO: i18n, downloading.
        #
        # self.extra is ignored now
        value=self._getFormValue() or None
        return self.template(name=self.context.__name__, value=value)

    def _toFieldValue(self, input):
        value=super(NamedFileWidget, self)._toFieldValue(input)
        if value is not self.context.missing_value:
            filename=getattr(input, "filename", None)
            contenttype=input.headers.get("content-type",
                                          "application/octet-stream")
            value=NamedFile(value, contenttype, filename)

        return value
    
    def hasInput(self):
        return ((self.name+".used" in self.request.form)
                or
                (self.name in self.request.form)
                ) and not self.request.form.get(self.name+".nochange", '')


class NamedFileDisplayWidget(DisplayWidget):
    template = ViewPageTemplateFile('displaywidget.pt')
    
    def __call__(self):
        if self._renderedValueSet():
            value = self._data
        else:
            value = None
        return self.template(name=self.context.__name__, value=value)
