#!/usr/bin/python
# -*- coding: utf-8 -*-

# Librairie pysnmp
import sys
import os
import socket
import struct
import string
import regex
from netaddr import EUI, mac_bare, mac_cisco, mac_eui48, mac_unix, mac_unix_expanded, mac_pgsql, NotRegisteredError, AddrFormatError
from ipaddress import ip_address, ip_network, IPv4Address, IPv4Interface, AddressValueError
from UtilsDR.printFmt import prtErr

# Choisir les modules a exporter
__all__ = ['isSystemUnix', 'getNomService', 'testIpMasque',
           'getNetProtocol', 'getPortService',
           'macFormat', 'test_mac', 'getFormatMac', 'testMacFormat', 'testUser'
           ]


def isSystemUnix():
    # Verification que le le systeme est un dérivé d'unix.
    # (linux, xbsd, mac)
    if (sys.platform.startswith('linux') or
        sys.platform.startswith('freebsd') or
        sys.platform.startswith('netbsd') or
            sys.platform == 'darwin'):
        return True
    else:
        return False


class drip(object):
    """
        http://sametmax.com/la-difference-entre-__new__-et-__init__-en-python/
    """
    def __new__(cls, ipvalue):
        # print("new")
        if cls.__IsValid(ipvalue):
            return super(drip, cls).__new__(cls)
        else:
            return None

    def __init__(self, ipvalue='127.0.0.1'):

        self.ip = ip_network(ipvalue, strict=False)
        self.host = str(IPv4Address(ipvalue.split('/')[0]))
        self.host_dec = int(IPv4Address(self.host))
        self.host_hex = hex(self.host_dec)
        self.network = self.ip.network_address
        self.mask = str(self.ip.netmask)
        self.mask_bin = ".".join(map(str,["{0:08b}".format(int(x)) for x in str(self.mask).split(".")]))
        self.maskbits = self.ip.prefixlen
        self.host_bin =  ".".join(map(str,["{0:08b}".format(int(x)) for x in str(self.host).split(".")]))
        self.ipversion = self.ip.version
        self.is_multicast = self.ip.is_multicast
        self.is_unicast = not self.ip.is_multicast
        self.is_private = self.ip.is_private
        self.is_global = self.ip.is_global
        self.is_unspecified = self.ip.is_unspecified
        self.is_reserved = self.ip.is_reserved
        self.is_loopback = self.ip.is_loopback
        self.is_link_local = self.ip.is_link_local
        self.is_public = self.is_unicast and not self.is_private

        self.nb_adresses = self.ip.num_addresses
        self.broadcast = self.ip.broadcast_address
        self.with_netmask = IPv4Interface(str(self.ip)).with_netmask
        self.with_hostmask = IPv4Interface(str(self.ip)).with_hostmask
        # print("init ", self.ip)


    def __IsValid(ipvalue):
        try:
            tmp = ip_network(ipvalue, strict=False)
            # print('valid Ok')
            return True
        except ValueError:
            # print('valid KO')
            return False

    def get_ListHosts(self):
        return list(ip_network(str(self.ip)).hosts())

    def get_ListHosts_str(self):
        tmp_l = list()
        for bcl in list(ip_network(str(self.ip)).hosts()):
            #print(str(bcl))
            tmp_l.append(str(bcl))

        return tmp_l

    def get_listSubnets(self, prefix):
        try:
            return list(ip_network(self.ip).subnets(new_prefix=prefix))
        except ValueError:
            return None

def testIpMasque(ipvalue):
    try:
        tmp = ip_network(ipvalue, strict=False)
        # print('valid Ok')
        return True
    except ValueError:
        # print('valid KO')
        return False


def bits2netmask(bits):
    """ Calcul IPv4 masque de bits en string"""
    mask = (1 << 32) - (1 << 32 >> bits)
    return socket.inet_ntoa(struct.pack(">L", mask))


def getNetProtocol(protocole='tcp'):
    try:
        nameProto = socket.getprotobyname(protocole)
    except socket.error:
        return None

    else:
        return nameProto


def getNomService(service=80, protocole='tcp'):
    """Renvoi le nom du service.
        @port int
        @protocole str
        @retour nom du service
    """
    try:
        portNum = socket.getservbyport(service, protocole)
    except OSError:
        return None
    except TypeError:
        return None
    else:
        return portNum


def getPortService(service='http', protocole='tcp'):
    """Renvoi le port du service.
        @service    string
        @protocole  str
        @retour     port du service
    """
    if type(service) is str:
        service = service.lower().strip()

    try:
        portNum = socket.getservbyname(service, protocole)
    except OSError:
        return None
    except TypeError:
        return None
    else:
        return portNum

"""
class mac_custom(mac_unix): pass
mac_custom.word_fmt = '%.2X'
mac = EUI('00-1B-77-49-54-FD', dialect=mac_custom)
"""

def macFormat(macF):
    mac_options = {
        'CISCO': mac_cisco,
        'UNIXE': mac_unix_expanded,
        'BARE': mac_bare,
        'NORMAL': mac_eui48,
        'UNIX': mac_unix,
        'PGSQL': mac_pgsql
    }
    if macF.upper() in mac_options:
        return mac_options[macF.upper()]
    else:
        return mac_unix_expanded


def testMacFormat(macF):
    """Savoir si le format est dans la liste."""
    if macF and macF.upper() in ('CISCO', 'UNIXE', 'BARE', 'NORMAL', 'UNIX', 'PGSQL'):
        return macF
    else:
        return 'unixe'

def test_mac(user_input):
    """
    Test @ Mac
    """
    try:
        # Bloc à essayer
        l_input = regex.sub("[^a-zA-Z,0-9]","", user_input)
        l_input = l_input.ljust(12, '0')
        # print(f"MAC : {l_input}")
        mac = EUI(l_input)
        oui = mac.oui
        return mac
    except (NotRegisteredError, AddrFormatError):
        # Erreur adresse Mac non enregistrée !
        # Bloc qui sera exécuté en cas d'erreur
        oui = ""
        return oui
    else:
        # Erreur adresse Mac incorrecte !
        # Bloc qui sera exécuté en cas d'erreur
        oui = ""
        return oui

def getFormatMac(mac, FormatMac='unix'):
    """Format la mac adresse avec le format passé en argument."""
    _mac = EUI(mac)
    _mac.dialect = macFormat(FormatMac)

    return _mac


def testUser(user):
    if len(user) < 1 or len(user) > os.sysconf('SC_LOGIN_NAME_MAX'):
        return False
    for c in user:
        if c not in string.ascii_letters and \
           c not in string.digits and \
           c not in [".", "-", "_", "$"]:
            return False
    return True


"""
------[ Main ]---------
"""


def main():
    # Debut des tests
    print('')
    print("ce PC est un dérivé d'Unix : ", isSystemUnix())
    # Debut des tests @Mac
    print('')
    _mac = ""
    print(f"Cette @mac {_mac} est correct ? :", test_mac(_mac))
    _mac = "00:d8:61:84:6f:1a"
    print("Format Normal : ", getFormatMac(_mac, 'normal'))
    print("Format Cisco : ", getFormatMac(_mac, 'cisco'))
    print("Format unix : ", getFormatMac(_mac, 'unix'))
    print("Format unix E : ", getFormatMac(_mac, 'unixE'))

    print(f"Cette @mac {_mac} est correct ? :", test_mac(_mac))
    _mac = "00:d8:61:992:22"
    print(f"Cette @mac {_mac} est correct ? :", test_mac(_mac))
    # Debut des tests @IP
    print('')
    _ip = "127.0.0.1"
    print(f"L'adresse IP {_ip} est correcte : ", testIP(_ip))
    _ip = "100.358.0.1"
    print(f"L'adresse IP {_ip} est correcte : ", testIP(_ip))
    print('')
    print('-='*20)
    monip = '192.258.1.25/24'
    _ip = drip(monip)
    # print(_ip)
    if _ip:
        print(_ip)
        print("Host : ", _ip.host)
        print("Reseau : ", _ip.network)
        print("Masque : ", _ip.maskbits)
        print("Version ip : ", _ip.ipversion)
    else:
        prtErr(f"L'adresse {monip} est non valide")
    print('')
    monip = '192.255.1.25/16'
    _ip = drip(monip)
    # print(_ip)
    if _ip:
        print(_ip)
        print("Host : ", _ip.host)
        print("Reseau : ", _ip.network)
        print("Masque : ", _ip.maskbits)
        print("Version ip : ", _ip.ipversion)
    else:
        prtErr(f"L'adresse {monip} est non valide")
    print('')
    monip = '10.155.1.240'
    _ip = drip(monip)
    # print(_ip)
    if _ip:
        print(_ip)
        print("Host : ", _ip.host)
        print("Reseau : ", _ip.network)
        print("Masque : ", _ip.maskbits)
        print("Version ip : ", _ip.ipversion)
    else:
        prtErr(f"L'adresse {monip} est non valide")
    print('-='*20)
    _bits = 24
    print(f"Bits {_bits} correspond au masque : ", bits2netmask(_bits))

    # Debut des tests Port / Protocole
    # _port = 22
    print('')
    _proto = "SSH"
    print(f"Le protocole {_proto} a le port : ", getPortService(_proto))
    _proto = 17
    print(f"Le protocole {_proto} a le port : ", getPortService(_proto))
    _port = 80
    print(f"Le port {_port} correspond au protocole : ", getNomService(_port))
    _port = 8018
    print(f"Le port {_port} correspond au protocole : ", getNomService(_port))
    print('')
    _proto = "TCP"
    print(f"Le protocole {_proto} a comme id : ", getNetProtocol(_proto))
    _proto = "udp"
    print(f"Le protocole {_proto} a comme id : ", getNetProtocol(_proto))
    _proto = "toto"
    print(f"Le protocole {_proto} a comme id : ", getNetProtocol(_proto))
    print('')
    _user = 'toto'
    if testUser(_user):
        print(f"Le user {_user} est valable.")
    else:
        prtErr(f"Le user {_user} n'est pas valable.")
    _user = 'to_to!'
    if testUser(_user):
        print(f"Le user {_user} est valable.")
    else:
        prtErr(f"Le user {_user} n'est pas valable.")


if __name__ == "__main__":
    main()
