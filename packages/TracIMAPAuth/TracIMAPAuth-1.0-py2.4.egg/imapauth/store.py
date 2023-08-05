import imaplib

from trac.core import *
from trac.config import Option, IntOption, BoolOption

from acct_mgr.api import IPasswordStore

class IMAPStore(Component):
    """An AccountManager backend to use IMAP."""
    
    server_host = Option('imap', 'server', default='localhost',
                         doc='Server to use for IMAP connection')
                         
    server_port = IntOption('imap', 'port', default=143,
                            doc='Port to use for IMAP connection')
    
    use_ssl = BoolOption('imap', 'ssl', default=False,
                         doc='Should the connection use SSL')
    
    implements(IPasswordStore)
    
    def check_password(self, user, password):
        try:
            cls = {False: imaplib.IMAP4, True: imaplib.IMAP4_SSL}[self.use_ssl]
            m = cls(self.server_host, self.server_port)
            m.login(user, password)
            return True
        except imaplib.IMAP4.error:
            return False
