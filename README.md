UtilsDR - Ensemble de modules et class en Python
================================================

Ce module regroupe des classes pour gérer : 
        - Les fichiers, 
        - Les Logs, 
        - Affichage Formatté 
        - Les infos Geoip d'un domaine ou d'une @IP.

Vous pouvez l'installer avec pip:

    pip install UtilsDR

Exemple d'usage:

    >>> from UtilsDR.utils import UtilsFichier
    >>> FicUtil = UtilsFichier()
    >>> FicUtil.isCheminExiste(nomFic)

Ce code est sous licence MIT.
