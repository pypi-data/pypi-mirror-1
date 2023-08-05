from zope.app.form.browser import widget
from p4a.fileimage import file

class ImageDisplayWidget(file.FileDownloadWidget):
    """Widget capable of displaying an image file.
    """
    
    @property
    def base_url(self):
        contentobj = self.context.context.context
        return contentobj.absolute_url() + '/viewimage'

    def __call__(self):
        if not self._data:
            return widget.renderElement(u'span',
                                        cssClass='image-absent',
                                        contents='No image set')
        
        url = self.url
        
        field = self.context
        extra = {}

#        XXX We do not want preferred_dimensions. Get the actual dimensions!
#            But, how is that done?         
#        if field.preferred_dimensions is not None:
#            extra['width'], extra['height'] = field.preferred_dimensions

        return widget.renderElement(
            u'img',
            src=url,
            **extra)

class ImageURLWidget(file.FileDownloadWidget):
    """Widget that returns the URL of the image
       This is clearly overkill, but it was the easy way to get
       something working fast.
       Revisit the consumer of this class and probably 
       access the url inline there.
    """
    
    @property
    def base_url(self):
        contentobj = self.context.context.context
        return contentobj.absolute_url() + '/viewimage'

    def __call__(self):
        if not self._data:
            return widget.renderElement(u'span',
                                        cssClass='image-absent',
                                        contents='No image set')
        
        return self.url
        
