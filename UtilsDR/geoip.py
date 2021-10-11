#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Script Permettant de connaitre les information d'une @IP.

Ce Module Permet à partir d'une adresse Ip de connaitre :
    - Sa position Géographique,
    - l'AS auquel il appartient,
    - Le nom de l'organisation

Example:
    Examples can be given using either the ``Example`` or ``Examples``
    sections. Sections support any reStructuredText formatting, including
    literal blocks::

        $ python geoip_lookup.py

Section breaks are created by resuming unindented text. Section breaks
are also implicitly created anytime a new section starts.

Attributes:
    module_level_variable1 (int): Module level variables may be documented in
        either the ``Attributes`` section of the module docstring, or in an
        inline docstring immediately following the variable.

        Either form is acceptable, but the two should not be mixed. Choose
        one convention to document module level variables and be consistent
        with it.

Installation des dépendance maxmind :
    pip install maxminddb
    pip install maxminddb-geolite2

Todo:
    * Ajout liste des entrées DNS pour les MX
    * Faire le tri dans les fonctions

.. _Google Python Style Guide:
   http://google.github.io/styleguide/pyguide.html
   https://realpython.com/documenting-python-code/

"""
from UtilsDR.utils import UtilsFichier
from UtilsDR.log import initLog, LOG_INFO, LOG_DEBUG, LOG_WARN, LOG_ERROR
# from UtilsDR.printFmt import *
from UtilsDR.version import __version__
from console import fg, bg, fx
import socket
# import re
import dns.resolver
import dns.name
import dns.reversename
import geoip2.database
import ipaddress
"""
from urllib.parse import urlparse, urlsplit

b = urlsplit('//www.cwi.nl/%7Eguido/Python.html')
>>> b
SplitResult(scheme='', netloc='www.cwi.nl',
            path='/%7Eguido/Python.html', query='', fragment='')
>>> b.netloc.split(':')[0].split('.')[-2:]
['cwi', 'nl']
>>> '.'.join(uu)
'cwi.nl'

"""


"""------[ Regex ]---------"""
# _RGX_IPV4ADDR = re.compile(r'^(?P<addr>\d+\.\d+\.\d+\.\d+)')

"""------[ Vars ]---------"""
_debug = False
# __version__ = "1.6"

"""
------[ Class ]---------
"""


class Geoip():
    """Permet de requeter dans les fichier de BDD Maxmind.

    The __init__ method may be documented in either the class level
    docstring, or as a docstring on the __init__ method itself.

    Note:
        Do not include the `self` parameter in the ``Args`` section.

    Args:
        ip_address (str): Chaine contenant une @IP.

    Attributes:
        msg (str): Human readable string describing the exception.

    """

    def __init__(self, ip_address="127.0.0.1"):
        """Initialisation de la classe."""
        self.ip_address = None
        self.Error = True
        self.Domain = None
        self.Alias = None

        # Initialisation des logs et des messages d'erreur
        self.__ListErreurs = {
            'Erreur ip': 'Le parametre est incorrect. Ni une @IP ni un nom de domaine.',
            'Erreur loopback': 'Le parametre Ip est une adresse de Loopback',
            'Erreur BDD': "Un fichier de BDD est absent.",
            'Erreur BDD2': "Le fqdn est introuvable dans la BDD."
        }

        # logging.basicConfig(filename='geoip.log', level=logging.INFO,
        #                     format="%(asctime)-15s %(filename)s:%(lineno)-4d %(funcName)s %(levelname)s:%(message)s")
        initLog('Geoip')
        LOG_INFO("--- Lancement de la classe Geoip")
        LOG_INFO("Param : " + ip_address)

        # TODO: Test d'une URL et parsing
        # TODO: Test avec @IP 47.56.132.146

        # Tests de la valeur en entrée
        if not self.isIP(ip_address) and not self.setDomain(ip_address):
            LOG_ERROR(self.__ListErreurs['Erreur ip'])
            raise AttributeError(self.__ListErreurs['Erreur ip'])

        if self.isIP(ip_address):
            self.setDomain(ip_address)
            # print(self.ip_address)

        if self.TestIpPublic(self.ip_address):
            if self.__ClassInit():
                LOG_INFO("__ClassInit : OK")
            else:
                LOG_DEBUG("__ClassInit : Erreur")
                raise AttributeError(self.__ListErreurs['Erreur BDD2'])

            self.Error = False
        else:
            """Erreur Ip / domain non valide."""
            # self.Error = True
            LOG_ERROR(self.__ListErreurs['Erreur loopback'])
            raise AttributeError(self.__ListErreurs['Erreur loopback'])
            return None

    def __bool__(self):
        return self.Error

    def __ClassInit(self):
        """Intialisation de la classe si les vérifications sont OK."""
        # Ouverture des databases locales.
        # Creation d'un objet Reader. En utilisant le même objet
        # pour de multiple requetes, cela évite des ouvertures couteuses en temps.
        if not self.ouvreBDD():
            LOG_ERROR(self.__ListErreurs['Erreur BDD'])
            raise AttributeError(self.__ListErreurs['Erreur BDD'])
            return False

        self.t_EU = ""
        if self.Continent_Code == 'EU':
            try:
                if self.repCity.country.is_in_european_union:
                    self.t_EU = ' (Pays faisant partie de l\'EU)'

            except BaseException:
                self.t_EU = ""
            # else:
            #     self.t_EU = ""
            #     print("888")

        # On met le nom du pays dans la langue originale.
        if self.Pays_Code != "FR":
            payscode = self.Pays_Code.lower() if self.Pays_Code is not None else 'en'
            if payscode == 'us':
                payscode = 'en'
            elif payscode == "cn":
                payscode = "zh-CN"

            try:
                LOG_INFO("Nom du pays : {}".format(
                    self.repCity.country.names[payscode]))
                self.t_EU = " (" + \
                    self.repCity.country.names[payscode] + ")"
            except KeyError as err:
                LOG_DEBUG("Erreur Cle non trouvé : {}.".format(err))
                return False

        self.Time_Zone = self.repCity.location.time_zone
        self.Postal_Code = self.repCity.postal.code
        self.Ville = self.repCity.city.name
        if self.repCity.subdivisions:
            self.Region = self.repCity.subdivisions[0].names
            self.Departement = self.repCity.subdivisions.most_specific.names
        else:
            self.Region = ""
            self.Departement = ""

        # print(self.Departemt)
        self.Lat = self.repCity.location.latitude
        self.Long = self.repCity.location.longitude

        self.AS_Number = self.repAsn.autonomous_system_number
        self.AS_Organisme = self.repAsn.autonomous_system_organization
        self.AS_Network = self.repAsn.network

        return True

    def isIP(self, s_ip):

        try:
            l_ip = ipaddress.IPv4Address(s_ip)
        except ipaddress.AddressValueError:
            return False
        else:
            return True

    def TestIpPublic(self, s_ip):

        if self.isIP(s_ip):
            l_ip = ipaddress.IPv4Address(s_ip)
            if l_ip.is_private or \
                    l_ip.is_loopback or \
                    l_ip.is_multicast or \
                    l_ip.is_reserved or \
                    l_ip.is_unspecified:
                return False
            else:
                self.ip_address = l_ip
                return True

    def __getDomainIP(self, fqdn):
        """Place les valeurs IP."""
        return socket.gethostbyname_ex(fqdn)[2][0]

    def __getDomainName(self, fqdn):
        """Retourne la valeur IP du Domaine."""
        if self.isIP(fqdn):
            try:
                tmp = socket.gethostbyaddr(fqdn)[0]
                LOG_INFO(tmp)
                return tmp
            except socket.herror:
                LOG_ERROR(fqdn)
                return fqdn

        else:
            return socket.gethostbyname_ex(fqdn)[0]

    def __getDomainAlias(self, fqdn):
        """Place les valeurs IP."""
        alias = ("" if len(socket.gethostbyname_ex(fqdn)[
            1]) == 0 else socket.gethostbyname_ex(fqdn)[1][0])
        return alias

    def setDomain(self, fqdn):
        """Recherche le fqdn a partir du hostname ou @IP.

        Parameters
        ----------
        fqdn : str
            Le nom DNS à traiter

        Raises
        ------
        BaseException
            Si le fqdn est incorrect, on retourne None

        Returns
        -------
        list
            une liste de strings : Nom Domain / alias / @IP

        """
        if fqdn == "":
            return False
        try:
            self.Domain = self.__getDomainName(fqdn)
            self.Alias = self.__getDomainAlias(fqdn)
            self.ip_address = self.__getDomainIP(fqdn)
            return True
        except BaseException:
            return False

    def ouvreBDD(self):

        __RepBDD = '/usr/local/GeoiP/'
        __BDDVille = __RepBDD + 'GeoLite2-City.mmdb'
        __BDDPays = __RepBDD + 'GeoLite2-Country.mmdb'
        __BDDASN = __RepBDD + 'GeoLite2-ASN.mmdb'

        # Test Presence du repertoire
        FicUtil = UtilsFichier()
        if not FicUtil.isCheminExiste(__RepBDD):
            return False

        # Ouverture
        readCity = geoip2.database.Reader(__BDDVille)
        self.repCity = readCity.city(self.ip_address)

        readCountry = geoip2.database.Reader(__BDDPays)
        self.repCountry = readCountry.country(self.ip_address)

        readAsn = geoip2.database.Reader(__BDDASN)
        self.repAsn = readAsn.asn(self.ip_address)

        self.Continent_Code = self.repCity.continent.code
        self.Pays_Code = self.repCity.country.iso_code

        # Fermeture des BDD
        readAsn.close()
        readCity.close()
        readCountry.close()

        return True

    def getCountryCode(self):
        """Code du Pays.

        Returns:
        --------
        str
            contenant le Code du Pays.
        """

        return self.Pays_Code

    def getCountry(self):
        """Renvoie le Nom du Pays."""
        return self.repCity.country.names['fr'] + self.t_EU

    def getContinentCode(self):
        """Renvoie le le Code du Continent."""
        return self.Continent_Code

    def getContinent(self):
        """Renvoie le Nom du Continent."""
        return self.repCity.continent.names['fr']

    def getRegion(self, Lang='fr'):
        """Renvoie le Nom de l'état / Région."""
        if self.Region:
            return self.Region[Lang]
        else:
            return ""

    def getDepartement(self, Lang='fr'):
        """Renvoie le Nom du Departement."""
        if self.Departement:
            return self.Departement[Lang]
        else:
            return ""

    def getCoordonnees(self):
        """Renvoie la Lat et la Long."""
        return "Latitude : {:.4f}, Longitude : {:.4f}".format(self.Lat, self.Long)

    def getPostalCode(self):
        """Renvoie le Code postal."""
        return self.Postal_Code if self.Postal_Code else ""

    def getVille(self):
        """Renvoie le nom de la Ville."""
        return self.Ville if self.Ville else ""

    def getTimeZone(self):
        """Renvoie la Time Zone."""
        return self.Time_Zone

    def getASnumber(self):
        """Renvoie le Numero d'AS."""
        return self.AS_Number

    def getASorganisation(self):
        """Renvoie le nom de l'organisation."""
        return self.AS_Organisme

    def getASnetwork(self):
        """Renvoie le réseau IP associé."""
        return self.AS_Network

    def getVersion(self):
        """Renvoie le numéro de version du Module."""
        return "version de {} : {}".format(__file__.split('/')[-1], __version__)


"""
------[ Fonctions ]---------
"""


def getMX(domain):
    """Affiche les MX du domain."""
    answers = dns.resolver.query(domain, 'MX')
    for rdata in answers:
        print(
            'Le Host',
            rdata.exchange,
            'a comme preference',
            rdata.preference)
    return "OK"
