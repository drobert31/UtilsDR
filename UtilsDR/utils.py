#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
from pathlib import Path
import shutil

"""------[ Class ]---------"""


class UtilsFichier():

    def __init__(self, repertoire='', fichier=''):
        self.c_fic = fichier
        self.c_dir = repertoire

    def isCheminExiste(self, c_dir="") -> bool:
        """Test si le répertoire existe."""
        if not os.path.exists(c_dir):
            print("Le fichier n'existe pas ou est introuvable.")
            return False
        else:
            return True

    def isFichierExiste(self, c_fic, c_dir="") -> bool:
        """Test si le fichier existe."""
        if not os.path.isfile(os.path.join(c_dir, c_fic)):
            print("Le répertoire n'existe pas ou est introuvable.")
            return False
        else:
            return True

    def FichierExiste(self, c_fic, c_dir):
        if not (os.path.exists(os.path.join(c_dir, c_fic)) and os.path.isfile(os.path.join(c_dir, c_fic))):
            print("Le fichier ou le répertoire n'existe pas ou est introuvable.")
            # sys.exit()
        else:
            return True

    # Lecture du fichier de configuration
    def ChargeFic(self, c_fic, c_dir):
        try:
            file = open(os.path.join(c_dir, c_fic))
            result = file.read()
            file.close()
            return result
        except OSError:
            # print(e, file=sys.stderr)
            err = "Fichier non trouvé"
            print("\n")
            print("Impossible de Lire le Fichier ({}), le script se termine.".format(err))
            print("\n")
            # sys.exit(1)
        except Exception as ex:
            print(ex)
            print("Impossible de continuer (%s), le script se termine.")
            # TODO: A ajouter un raise
            quit()

    def CreerRep(self, c_dir):
        """Creation du repertoire output directory si manquant.

        a voir :
        Path('/my/directory').mkdir(mode=0o777, parents=True, exist_ok=True)
        This recursively creates the directory and does not raise an exception if the directory already exists.
        """
        if not os.path.exists(c_dir):
            os.mkdir(c_dir)

    def EcritFic(self, c_fic, c_dir="", c_Content="", c_mode='w'):
        """Ecrit c_Content dans un fichier."""
        if c_Content:
            f = open(os.path.join(c_dir, c_fic), c_mode)
            f.write(c_Content)
            f.close()

    def CopyFic(self, c_fic, c_ficdest):
        """Copie un fichier vers un autre."""
        new_file = shutil.copy(c_fic, c_ficdest, follow_symlinks=False)
        if new_file == c_ficdest:
            return True

    def MoveFic(self, c_fic, c_dest):
        """Move un fichier vers un autre fichier ou un répertoire."""
        shutil.move(c_fic, c_dest, copy_function='copy2')

    def EffaceFic(self, c_fic):
        """Effacer un Fichier."""
        file_path = Path(c_fic)
        file_path.unlink()

    def getListRep(self, c_dir='.'):
        """Retourne la liste des répertoires présent dans c_dir."""
        p = Path(c_dir)
        tmp = [x for x in p.iterdir() if x.is_dir()]
        cc = list()
        for bcl in tmp:
            cc.append(os.fspath(bcl))

        return cc

    def getListFile(self, c_dir='.', c_filtre='*.py'):
        """Retourne la liste des Fichiers présent dans c_dir.

        Parameters
        ----------
        c_dir : str
            Le nom du répertoire source
        c_filtre : str
            Le filtre à appliquer

        Raises
        ------
        BaseException
            Si le fqdn est incorrect, on retourne None

        Returns
        -------
        list
            une liste de strings : Nom de Fichiers

        """
        p = Path(c_dir)
        cc = list()
        curList = list(p.glob(c_filtre))
        for bcl in curList:
            if bcl.is_file():
                cc.append(os.fspath(bcl))

        return cc
