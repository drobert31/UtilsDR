#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Script Permettant de formatter l'affichage.

Ce Module Permet de formatter la chaine avant affichage :

"""

from console import fg, bg, fx
from os import linesep

# Choisir les modules a exporter
__all__ = ['prtFmt', 'prtParagraphe', 'prtN', 'prtItalic', 'prtErr']


def formatAffichage(libelle, value, larg=12):
    """Formatage avant affichage."""
    tmp = fx.bold + '{:<{larg}}'.format(libelle, larg=larg) + fx.end
    return tmp, value


def prtFmt(libelle, value, larg=12, sep=':', indent=5, indentchar=" "):
    """Affichage d'un couple de str séparé par un séparateur avec indentation."""
    tmp, value = formatAffichage(libelle, value, larg)
    print(indentchar * indent +
          "{libelle} {sep} {value}".format(libelle=tmp, value=value, sep=sep))


def prtParagraphe(texte, marge=20, sautApres=False):
    """Affiche un paragraphe multiligne avec marge."""
    for ligne in texte.split("\n"):
        print(" " * marge, ligne.strip())

    if sautApres:
        print(linesep)


def prtN(texte=""):
    """Idem print avec saut de ligne."""
    print(texte + linesep)


def prtItalic(texte, sautApres=False):
    """Affiche un texte en Italique."""
    print(textItalic(texte))


def textItalic(texte=""):
    """Retourne un texte en Italique."""
    return fx.italic(texte)


def prtErr(texte=""):
    """Affichage un texte d'erreur."""
    print(fx.bold + fg.RED + texte + fx.end)
