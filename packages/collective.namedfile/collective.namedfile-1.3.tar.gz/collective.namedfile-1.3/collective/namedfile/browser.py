from zope.publisher.browser import BrowserView
from zope.interface import implements
from zope.publisher.interfaces import IPublishTraverse
from zope.component import getMultiAdapter
from zope.publisher.interfaces import NotFound
import mimetypes
import os.path

class UrlDispatcher(BrowserView):
    """http://wiki.zope.org/zope3/HowDoIGrabVariablesFromArbitraryURLs
    """
    implements(IPublishTraverse)
    def __init__(self, context, request):
        super(UrlDispatcher, self).__init__(context, request)
        self.traverse_subpath = []

    def publishTraverse(self, request, name):
        self.traverse_subpath.append(name)
        return self
        

class FileViewDispatcher(UrlDispatcher):
    """View on a form to expose files for downloading.
    
    Registered as zope.Public, so it needs to check security manually. This is
    done by attempting to restrictedTraverse to the form (self.context) from
    the form's context (self.context.context). This probably restrticts this
    view to zope2.
    
    Subpath is fieldname or fieldname/filename
    Only the field is observed, but allowing the filename allows creation of
    better link urls.
    """
    
    def __call__(self):
        # Security check must be made here rather than in __init__
        # unicode paths are not allowed
        self.context.context.restrictedTraverse(str('@@'+self.context.__name__))
        
        if not self.traverse_subpath:
            raise NotFound(self, '', self.request)
        field_name = self.traverse_subpath[0]
        self.context.setUpWidgets(ignore_request=True)
        widget = self.context.widgets[field_name]
        file = widget._data
        if getattr(file, 'filename', None):
            extension = os.path.splitext(file.filename)[1].lower()
            contenttype = mimetypes.types_map.get(extension,
                                                  "application/octet-stream")
        elif file.contentType:
            contenttype = file.contentType
        else:
            contenttype = "application/octet-stream"
        self.request.response.setHeader("Content-Type", contenttype)
        self.request.response.setHeader("Content-Length", file.getSize())
        return file.data


class FileView(BrowserView):
    '''
    View a file field. Your subclass should define a form_field attribute.
    '''
    
    def __call__(self):
        form_field = self.form_field.bind(self.context)
        file = form_field.get(self.context)
        if file.filename:
            extension = os.path.splitext(file.filename)[1].lower()
            contenttype = mimetypes.types_map.get(extension,
                                                  "application/octet-stream")
        elif file.contentType:
            contenttype = file.contentType
        else:
            contenttype = "application/octet-stream"
        self.request.response.setHeader("Content-Type", contenttype)
        self.request.response.setHeader("Content-Length", file.getSize())
        return file.data


class FileDownloadView(FileView):
    '''
    Download a file field. Your subclass should define a form_field attribute.
    '''
    
    def __call__(self):
        form_field = self.form_field.bind(self.context)
        file = form_field.get(self.context)
        self.request.response.setHeader(
            "Content-Disposition", "attachment; filename=%s" % file.filename)
        return FileView.__call__(self)
