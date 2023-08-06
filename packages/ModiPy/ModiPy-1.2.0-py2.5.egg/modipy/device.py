"""
A generic Device definition to use for change targets.
"""
import socket
import logging
import debug

log = logging.getLogger('modipy')

class Device:

    """
    A Device provides an abstraction of a device that can
    be manipulated by Modipy. They are manipulated via a
    Provisioner that knows how to communicate with the device.

    You can add extra configuration information for a device
    when defining its configuration. You just add extra
    configuration names and they are set as attributes of the Device.

    e.g.: To define a Device specific 'telnet_password', you
    would add the following XML as a child of <device/>:
    <telnet_password>mypassword</telnet_password>
    """

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
        self.zapi_port = '443'
        
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



