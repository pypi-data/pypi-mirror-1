from repoze.what.predicates import Predicate
from ipaddr import IPv4 as IP #: Googles ipaddr.py
from types import ListType

import logging
log = logging.getLogger(__name__)

class ip_from(Predicate):
    """ Only allow access to specified IPs """
    
    message = "Unauthorized Access" #: default message
    
    def __init__(self, allowed=None, message=None, **kwargs):
        """
        @param allowed: the ip or list of ips allowed to access the wsgi server 
        @param message: The message to return when check fails 
        """
        
        allowed = [allowed] if type(allowed) is not ListType else allowed 
        
        self.message = message if message else self.message
        self.allowed = [IP(x) for x in allowed]
        super(ip_from, self).__init__(**kwargs)

    def evaluate(self, environ, credentials):
        """ 
        check that the request ip in the allowed list 
        @return: Boolean
        """
        
        remote = IP(environ.get("REMOTE_ADDR", "0.0.0.0"))
    
        if True not in [(remote in x) for x in self.allowed]:
            log.warn("Failed Access Attempt by: %s" % environ.get("REMOTE_ADDR", "0.0.0.0"))  
            self.unmet(self.message)
