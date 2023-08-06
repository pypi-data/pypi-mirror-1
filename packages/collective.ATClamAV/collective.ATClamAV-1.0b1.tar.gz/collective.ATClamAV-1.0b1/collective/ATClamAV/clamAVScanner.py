from collective.ATClamAV.interfaces import IAVScanner
from zope.interface import implements
import socket

class ClamAVScanner(object):
    """
    """
    implements(IAVScanner)
    
    
    def ping(self,host='localhost',port=3310):
        """
        """
        s = self.__init_socket__(host,port)

        try:
            s.send('PING')
            result = s.recv(20000)
            s.close()
        except:
            raise 'ScanError', 'Could not ping clamd server'

        if result=='PONG\n':
            return True
        else:
            raise 'ScanError', 'Could not ping clamd server'

        
    def scanBuffer(self,buffer,host='localhost',port=3310):
        """Scans a buffer for viruses
        """
        s = self.__init_socket__(host,port)

        s.send('STREAM')
        sport = int(s.recv(200).strip().split(' ')[1])
        n=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        n.connect((host, sport))
        
        sended = n.send(buffer)
        n.close()

        if sended<len(buffer):
            raise 'BufferTooLong'

        result='...'
        while result!='':
            result = s.recv(20000)
            if len(result)>0:
                virusname = result.strip().split(':')[1].strip()
                if virusname[-5:]=='ERROR':
                    raise 'ScanError', virusname
        s.close()
        if virusname=='OK':
            return None
        else:
            return virusname

    def __init_socket__(self,host,port):
        """
        """

        s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.connect((host, port))
        except socket.error:
            raise 'ScanError', 'Could not reach clamd on (%s:%s)' % (host, port)
        return s
        