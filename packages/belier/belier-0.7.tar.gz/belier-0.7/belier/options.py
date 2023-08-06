# -*- coding: utf-8 -*-
# Copyright (C) [2008] [Carl Chenet]
# Ce programme est un logiciel libre ; vous pouvez le redistribuer et/ou le
# modifier au titre des clauses de la Licence Publique Générale GNU, telle que
# publiée par la Free Software Foundation ; soit la version 2 de la Licence,
# ou (à votre discrétion) une version ultérieure quelconque.
#
# Ce programme est distribué dans l'espoir qu'il sera utile, mais SANS AUCUNE
# GARANTIE ; sans même une garantie implicite de COMMERCIABILITE ou DE
# CONFORMITE A UNE UTILISATION PARTICULIERE.
#
# Voir la Licence Publique Générale GNU pour plus de détails. Vous devriez
# avoir reçu un exemplaire de la Licence Publique Générale GNU avec ce
# programme ; si ce n'est pas le cas, écrivez à la Free Software Foundation
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.

#Extraction des options de la ligne de commande
"""Options de la ligne de commande"""

from os.path import exists, abspath, isdir, isfile, expanduser
from optparse import OptionParser
import sys

class Options:
    """Extrait les options de la ligne de commande"""

    def __init__(self):
        self.options = ()
        parser = OptionParser(version="%prog 0.7")
        self.definit_options(parser)
        self.teste_options()

    def definit_options(self, parser):
        """Définition des options"""
        parser.add_option("-e", "--entree", dest="nomfichier",
            action="store", type="string",
            help=u"contient les ordres pour générer le ou les scripts",
            metavar="FICHIER")
        parser.add_option("-s", "--repertoire-sortie", dest="repsortie",
            action="store", type="string",
            help=u"répertoire où entreposer les fichiers générés",
            metavar=u"RÉPERTOIRE")
        parser.add_option("-d", "--delai", dest="delai",
            action="store", type="int", default=2,
            help=u"en secondes pour exécuter une commande du script",
            metavar=u"DÉLAI")
        self.options = parser.parse_args()

    def teste_options(self):
        """Teste les options"""
        if self.options[0].nomfichier is not None:
            fichierentree = abspath(expanduser(self.options[0].nomfichier))
            if not exists(fichierentree):
                print "Le fichier %s n'existe pas." % fichierentree
                sys.exit(1)
            elif not isfile(fichierentree):
                print "%s n'est pas un fichier." % fichierentree
                sys.exit(1)
            else:
                self.options[0].nomfichier = fichierentree

        if self.options[0].repsortie is not None:
            repertoiresortie = abspath(expanduser(self.options[0].repsortie))
            if not exists(repertoiresortie):
                print "Le répertoire %s n'existe pas." % repertoiresortie
                sys.exit(1)
            elif not isdir(repertoiresortie):
                print "%s n'est pas un répertoire." % repertoiresortie
                sys.exit(1)
            else:
                self.options[0].repsortie = repertoiresortie    

        if self.options[0].delai is not None:
            if self.options[0].delai < -1 or self.options[0].delai > sys.maxint:
                print "La valeur indiqué n'est pas valide.\nLa valeur délai \
doit être >= -1 et <= valeur d'un entier sur votre système."
                sys.exit(1)
            
    def lesoptions(self):
        """Retourne les options de la ligne de commande"""
        return self.options

