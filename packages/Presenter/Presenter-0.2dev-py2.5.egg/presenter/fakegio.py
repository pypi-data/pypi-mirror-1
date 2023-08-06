FILE_ATTRIBUTE_STANDARD_ICON = 1
FILE_ATTRIBUTE_STANDARD_CONTENT_TYPE = 2

CONTENT_TYPE = {
    'mpg': 'video/mpeg',
    'mpeg': 'video/mpeg',
    'mpe': 'video/mpeg',
    
    'mpv2': 'video/mpeg2',
    'mp2v': 'video/mpeg2',
    
    'qt': 'video/quicktime',
    'mov': 'video/quicktime',
    
    'avi': 'video/x-msvideo',
    'movie': 'video/x-sgi-movie',
}

class FileIcon(object):
    def get_names(self):
        return self.names

class FileInfo(object):
    def get_icon(self):
        return self.icon
    
    def get_content_type(self):
        return self.content_type

class File(object):
    def __init__(self, uri):
        self.uri = uri

    def query_info(self, flags):
        fileinfo = FileInfo()

        if flags == FILE_ATTRIBUTE_STANDARD_ICON:
            icon = FileIcon()
            icon.names = ['text-x-plain']
            fileinfo.icon = icon
        elif flags == FILE_ATTRIBUTE_STANDARD_CONTENT_TYPE:
            extension = self.uri.rsplit('.', 1)[1]
            fileinfo.content_type = CONTENT_TYPE[extension]

        return fileinfo

    def get_basename(self):
        filepart = self.uri.rsplit('/', 1)[1]
        return filepart
