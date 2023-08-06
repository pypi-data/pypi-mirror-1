import os
import tempfile

def write_to_tempfile(fileobj):
    """Assumes the file obj is of type OFS.Image.File and will write
    it to a temporary file returning the filename of the temp file.  This
    writing mechanism uses raw attributes knowing the data may be of
    type pdata.
    """
    
    id = fileobj.id
    if callable(id):
        id = id()
    fd, filename = tempfile.mkstemp('_'+id)
    os.close(fd)
    fout = open(filename, 'wb')
    
    data = fileobj.data
    if isinstance(data, str):
        fout.write(data)
    else:
        pdata = data
        while pdata is not None:
            fout.write(pdata.data)
            pdata = pdata.next
    fout.close()

    return filename

def write_ofsfile_to_tempfile(obj, preferred_name=None):
    """Assumes the file obj is of type OFS.Image.File and will write
    it to a temporary file returning the filename of the temp file.  Uses
    the possibly acquired index_html method to fetch the file.  This
    is a little more compatible with objects that seem like OFS.Image.File
    instances.
    """

    filename = preferred_name
    if filename is None:
        filename = obj.id
        if callable(filename):
            filename = filename()
    fd, filename = tempfile.mkstemp('_'+filename)
    os.close(fd)
    fout = open(filename, 'wb')
    
    class TempResponse(object):
        def getHeader(self,n):
            pass
        def setHeader(self, n, v):
            pass
        def setBase(self, v):
            pass
        def write(self, d):
            fout.write(d)
    
    class TempRequest(object):
        environ = {}
        def get_header(self, n, default=None):
            if default is not None:
                return default
            return ''
    
    res = obj.index_html(TempRequest(), TempResponse())
    if res:
        if isinstance(res, str):
            fout.write(res)
        else:
            # assumes some sort of iterator
            for x in res:
                fout.write(x)

    fout.close()

    return filename
