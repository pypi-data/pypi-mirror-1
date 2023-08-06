from repoze.what.predicates import Predicate                                                                                           
from ipaddr import IPAddressIPValidationError, IPNetwork, IPv4Network, IPv6Network, IPAddress as IP #: Googles ipaddr.py               
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
        self.allowed = []
        for address in allowed:
            ip = None
            try:
                ip = IP(address)
            except IPAddressIPValidationError:
                try:
                    ip = IPNetwork(address)
                except:
                    pass
            if ip:
                self.allowed.append(ip)

        super(ip_from, self).__init__(**kwargs)

    def evaluate(self, environ, credentials):
        """
        check that the request ip in the allowed list
        @return: Boolean
        """

        remote = IP(environ.get("REMOTE_ADDR", "0.0.0.0"))
        log.debug("Remote IP: %s Attempting Access" % remote)
        validate = False
        for address in self.allowed:
            if (isinstance(address, (IPv4Network, IPv6Network)) and remote in address) or remote == address:
                log.debug("IP Validated")
                validate = True
                break

        if not validate:
            log.warn("Failed Access Attempt by: %s" % environ.get("REMOTE_ADDR", "0.0.0.0"))
            self.unmet(self.message)

