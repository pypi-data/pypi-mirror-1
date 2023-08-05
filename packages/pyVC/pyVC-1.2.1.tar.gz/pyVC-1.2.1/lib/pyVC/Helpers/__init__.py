"""This package contains the modules used for helpers.

A Helper is defined in pyVC as a process that is optional to the functionality of the 
virtual network and is confined to a single real Machine. Examples include DHCP servers,
LDAP and DNS servers, IP Interfaces, Routing and iptables rules.

Each module should contain one publicly instantiable object, named 'Helper'. 

Please consult the documentation of each helper module for argmument parameters.
The base Helper, which all other Helper objects derive from, can be instantiated as:
    helper = Helper(realmachine, network)
    realmachine = Machine
    network = [Network, ...]
"""
__revision__ = "$Revision: 216 $"

__all__ = ["DHCP", "IP", "Router"]
