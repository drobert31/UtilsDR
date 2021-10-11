#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Module pour executer des requetes DNS."""

from dns import resolver, name, reversename
from dns.resolver import NoAnswer, NoNameservers, Timeout, NXDOMAIN, YXDOMAIN
from dns.query import xfr
from dns.zone import from_xfr

from UtilsDR.thread import ThreadWithReturnValue

"""
        qname (dns.name.Name object or string) - the query name
        rdtype (int or string) - the query type
        rdclass (int or string) - the query class
        tcp (bool) - use TCP to make the query (default is False).
        source (IP address in dotted quad notation) -
           bind to this IP address (defaults to machine default IP).
        raise_on_no_answer (bool) - raise NoAnswer if there's no answer (defaults is True).
        source_port (int) - The port from which to send the message. The default is 0.

        resolve(qname, rdtype=<RdataType.A: 1>, rdclass=<RdataClass.IN: 1>,
         tcp=False, source=None, raise_on_no_answer=True, source_port=0, lifetime=None, search=None)
"""


def dns_resolv(host="www.google.fr", type='A', classe=''):
    """Resoudre le nom.

        En sortie :
            Liste si OK
            False si pas d'enregistrement
            None  si le domaine est inexistant

        Exceptions :
        Raises:
            Timeout - no answers could be found in the specified lifetime
            NXDOMAIN - the query name does not exist
            YXDOMAIN - the query name is too long after DNAME substitution
            NoAnswer - the response did not contain an answer and raise_on_no_answer is True.
            NoNameservers - no non-broken nameservers are available to answer the question.

    """
    resolv = resolver.Resolver()
    resolv.timeout = 1
    resolv.lifetime = 0.5

    ip_list = list()
    try:
        if classe == '':
            answers_ip = resolv.resolve(host, type, tcp=False)
        else:
            answers_ip = resolv.resolve(host, type, classe, tcp=False)
        for rdata in answers_ip:
            # print(rdata)
            ip_list.append(rdata.to_text())
        return ip_list
    except NoAnswer:
        # print("*** pas d'enregistrement A pour ", host, "***")
        return False
    except NoNameservers:
        return False
    except Timeout:
        return False
    except NXDOMAIN:
        # print("*** Le nom : ", host, "n'existe pas ***")
        return None
    except YXDOMAIN:
        # print("*** Le nom : ", host, "est trop long ***")
        return None


def dns_resolv_dict(host="www.google.fr"):
    """Resoudre les types A, AAAA, MX, TXT.
        En entree :
            host (str)

        En sortie :
            dict contenant les réponses
    """
    resultat = {'A': '', 'AAAA': '', 'MX': '', 'TXT': ''}

    test1 = ThreadWithReturnValue(target=dns_resolv, args=(host, 'A'))
    test2 = ThreadWithReturnValue(target=dns_resolv, args=(host, 'AAAA'))
    test3 = ThreadWithReturnValue(target=dns_resolv, args=(host, 'MX'))
    test4 = ThreadWithReturnValue(target=dns_resolv, args=(host, 'TXT'))
    ipv4 = test1.join()
    ipv6 = test2.join()
    ipMX = test3.join()
    ipTXT = test4.join()

    if ipv4:
        resultat['A'] = ipv4
    if ipv6:
        resultat['AAAA'] = ipv6
    if ipMX:
        resultat['MX'] = ipMX
    if ipTXT:
        resultat['TXT'] = ipTXT

    # // Resultat
    return resultat


def dns_ptr(ip_adresse='127.0.0.1'):
    """Requete PTR.
        en entree :
            @IP
        en sortie :
            list avec Enregistrement DNS
    """
    ip_list = list()
    errorDns = False

    try:
        nom = reversename.from_address(ip_adresse)
    except SyntaxError:
        print("Ip adresse incorrecte")
        errorDns = True
        return False

    result = dns_resolv(nom, 'PTR')
    for rdata in result:
        # print("---------------", rdata)
        if rdata:
            ip_list.append(rdata)

    return ip_list


def dns_chaos(bind='version.bind'):
    """Requete de la zone CHAOS.
        Le troisième paramètre CH permet d utiliser la classe CHAOS
        dig  @X.X.X.X +short chaos txt version.bind
    """
    result = dns_resolv(bind, 'TXT', 'CH')
    if not result:
        # print("Impossible de récupérer la version du serveur")
        return False
    else:
        return result


def dns_srv(domain='openldap.org', service='ldap', protocol='tcp'):
    ip_list = list()
    nom = "_{0}._{1}.{2}".format(service, protocol, domain)
    result = dns_resolv(nom, 'SRV')
    # print(type(result))
    if result:
        for rdata in result:
            ip_list.append(rdata)

        return ip_list
    else:
        return None


"""
http://www.chicoree.fr/w/Interroger_le_DNS_avec_Python

"""
