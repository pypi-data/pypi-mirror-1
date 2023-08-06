# -*- coding: utf-8 -*-
# Copyright © 2008 Carl Chenet <chaica@ohmytux.com>
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

#Extraction des options de la ligne de commande
"""Options de la ligne de commande"""

from os import linesep
from os.path import exists, abspath, isdir, isfile, expanduser
from optparse import OptionParser
import sys

class Options:
    """Extrait les options de la ligne de commande"""

    def __init__(self):
        self._options = ()
        parser = OptionParser(version="%prog 1.2")
        self.definit_options(parser)
        self.teste_options()

    def definit_options(self, parser):
        """Définition des options"""
        parser.add_option("-e", "--entree", dest="nomfichier",
            action="store", type="string",
            help=_("contains the orders to generate the script"),
            metavar=_("FILE"))
        parser.add_option("-s", "--repertoire-sortie", dest="repsortie",
            action="store", type="string",
            help=_("the directory to store generated scripts"),
            metavar=_("DIRECTORY"))
        parser.add_option("-d", "--delai", dest="delai",
            action="store", type="int", default=10,
            help=_("in seconds the time between each order execution"),
            metavar=_("DELAY"))
        self._options = parser.parse_args()

    def teste_options(self):
        """Teste les options"""
        if self._options[0].nomfichier is not None:
            fichierentree = abspath(expanduser(self._options[0].nomfichier))
            if not exists(fichierentree):
                print _("%s : no such file") % fichierentree
                sys.exit(1)
            elif not isfile(fichierentree):
                print _("%s is not a file") % fichierentree
                sys.exit(1)
            else:
                self._options[0].nomfichier = fichierentree

        if self._options[0].repsortie is not None:
            repertoiresortie = abspath(expanduser(self._options[0].repsortie))
            if not exists(repertoiresortie):
                print _("%s : no such directory") % repertoiresortie
                sys.exit(1)
            elif not isdir(repertoiresortie):
                print _("%s is not a directory") % repertoiresortie
                sys.exit(1)
            else:
                self._options[0].repsortie = repertoiresortie

        if self._options[0].delai is not None:
            if self._options[0].delai < -1 or \
                self._options[0].delai > sys.maxint:
                print _("The given value is not valid%sThe delay value \
must be >= -1 and <= value of an integer on your system" % linesep)
                sys.exit(1)
            
    def lesoptions(self):
        """Retourne les options de la ligne de commande"""
        return self._options

