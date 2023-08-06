from zope.interface import Interface
from zope import schema
from collective.ATClamAV import ATClamAVMessageFactory as _
    
class IAVScannerSettings(Interface):
    """
    """
    clamav_host = schema.ASCIILine(title=_(u"Scanner host"),
        description=_(u"The host running the antivirus server"),
        default = 'localhost',
        required = True)
    clamav_port = schema.Int(title=_(u"Scanner port"),
        description=_(u"The port on which the antivirus server listens"),
        default=3310,
        required = True)
        
class IAVScanner(Interface):
    """
    """
    def ping():
        """
        """
        pass

    def scanBuffer(buffer):
        """
        """
        pass        
