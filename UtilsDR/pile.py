#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Script Permettant de simuler une pile.

Ce Module Permet à partir d'une pile :
    - 
    
TODO:
-----
    - Ajout de merge :
        x= {'a':1,'b':2}
        >>> x
        {'a': 1, 'b': 2}
        >>> y = {'b': 7, 'c': 9}
        >>> y
        {'b': 7, 'c': 9}
        >>> z = {**x, **y}
        >>> z
        {'a': 1, 'b': 7, 'c': 9} 

"""

# Choisir les modules a exporter
__all__ = ['nbElt', 'push', 'pop', 'show',
           'get', 'getCles', 'triCle', 'mergeTri']

contenu = dict()


def push(e, p):
    global contenu
    if p in contenu:
        contenu[p] = contenu[p] + [e]
    else:
        contenu[p] = [e]


def nbElt(p):
    global contenu
    if p in contenu:
        return(len(contenu[p]))
    else:
        return(0)


def pop(p):
    global contenu
    if p in contenu and len(contenu[p]) > 0:
        top = contenu[p][-1]
        contenu[p] = contenu[p][:-1]
        return(top)
    else:
        print("pile.pop: ERREUR la pile %s est vide !" % p)


def show(p):
    global contenu
    if p in contenu:
        for e in contenu[p]:
            print(e, end=', ')
        print('')


def get(p):
    global contenu
    if p in contenu:
        return contenu[p]


def getCles():
    """Retourne l'ensemble des clé de la pile."""
    global contenu
    return contenu.keys()


def triCle(p):
    """tri d'une clé."""
    global contenu
    if p in contenu:
        contenu[p] = sorted(contenu[p])


def mergeTri(p, q):
    """merge + tri de 2 clés si elles existent."""
    global contenu
    if p in contenu and q in contenu:
        return list(set(contenu[p]) | set(contenu[q]))
