"""
A generic Device definition to use for change targets.
"""
import socket
import logging
import debug

log = logging.getLogger('modipy')

class Device:

    def __init__(self, name):
        self.name = name
        self.fqdn = None
        self.ipaddress = None
        self.namespace = {}

        # Default for NetApp devices
        self.zapi_username = 'root'
        self.zapi_password = 'netapp1'
        self.zapi_scheme = 'https'
        self.zapi_realm = 'Administrator'
        
    def __str__(self):
        """
        Return the most precise definition for the device
        """
        if self.ipaddress:
            return '%s' % self.ipaddress
        elif self.fqdn:
            return self.fqdn
        else:
            return self.name

    def get_ipaddress(self):
        """
        Return the IP address of the device, as a string
        """
        if self.ipaddress:
            return '%s' % self.ipaddress

        elif self.fqdn:
            try:
                ipaddr = socket.gethostbyname(self.fqdn)
                return ipaddr
            except socket.gaierror, e:
                log.error("Cannot get IP address for device '%s': %s", self.fqdn, e )
                raise
        else:
            try:
                ipaddr = socket.gethostbyname(self.name)
                return ipaddr
            except socket.gaierror, e:
                log.error("Cannot get IP address for device '%s': %s", self.name, e )
                raise



