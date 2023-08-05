import os
from p4a.fileimage import utils

class DownloadFile(object):
    """A view for downloading file content.
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        ifpackagename, ifname, fieldname = \
                       self.request.form.get('field', ':').split(':')
        ifpackage = __import__(ifpackagename, {}, {}, ifpackagename)
        iface = getattr(ifpackage, ifname)
        adapted = iface(self.context)
        value = getattr(adapted, fieldname)

        return value.index_html(self.request, self.request.response)

class ViewImage(DownloadFile):
    """A view for streaming image content.
    """
