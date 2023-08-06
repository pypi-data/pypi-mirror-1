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
            # when submitted a new file 'value' is a 'ZPublisher.HTTPRequest.FileUpload'
            
            siteroot = getUtility(ISiteRoot)
            settings = siteroot.portal_properties.clamav_properties
            scanner = getUtility(IAVScanner)
            
            value.seek(0)
            content = value.read()
            result = scanner.scanBuffer(content,settings.clamav_host,int(settings.clamav_port))
            if result:
                return "Validation failed, file is virus-infected. (%s)" % (result)
            else:
                return 1
        else:
            # if keeped existing file 'value' is a 'OFS.Image.File'
            return 1

