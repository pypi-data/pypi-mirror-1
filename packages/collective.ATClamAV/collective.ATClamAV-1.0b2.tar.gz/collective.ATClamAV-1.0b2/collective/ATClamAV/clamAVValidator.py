from Products.validation.interfaces import ivalidator
from collective.ATClamAV.interfaces import IAVScanner
from zope.component import getUtility

from Products.CMFCore.interfaces import ISiteRoot

class ClamAVValidator:
    __implements__ = (ivalidator,)

    def __init__(self, name):
        self.name = name

    def __call__(self, value, *args, **kwargs):
        if hasattr(value, 'seek'):
            # when submitted a new file 'value' is a 
            # 'ZPublisher.HTTPRequest.FileUpload'
            
            siteroot = getUtility(ISiteRoot)
            settings = siteroot.portal_properties.clamav_properties
            scanner = getUtility(IAVScanner)
            
            value.seek(0)
            content = value.read()
            result = ''
            try:
                if settings.clamav_connection == 'net':
                    result = scanner.scanBuffer(content,'net',
                        host=settings.clamav_host,
                        port=int(settings.clamav_port))
                else:
                    result = scanner.scanBuffer(content,'socket',
                        socketpath=settings.clamav_socket)
            except Exception:
                return "There was an error while checking the file " \
                "for viruses: Please contact your system administrator."
            
            if result:
                return "Validation failed, file is virus-infected. (%s)" % (result)
            else:
                return 1
        else:
            # if keeped existing file 'value' is a 'OFS.Image.File'
            return 1

