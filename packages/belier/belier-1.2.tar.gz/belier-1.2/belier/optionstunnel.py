# -*- coding: utf-8 -*-
# Copyright © 2008 Carl Chenet <chaica@ohmytux.com>
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

#Extraction des options du tunnel
"""Extraction des options du tunnel"""

import sys

class OptionsTunnel:
    """Extraction des options du tunnel"""

    def __init__(self, ligne):
        self._source = ''
        self._destination = ''
        self.parse_ligne(ligne)

    def parse_ligne(self, ligne):
        """Parse la ligne qui indique les numéros de ports"""
        if len(ligne.split()) != 2:
            print _('You should have two tunnel options arguments \
(source port and destination port)')
            sys.exit(1)
        for port in ligne.split():
            if not port.isdigit():
                print _('A port number should only contain digits')
                sys.exit(1)
            if int(port) > 65535:
                print _('A port number can not exceed 65535')
                sys.exit(1)
        self._source, self._destination = ligne.split()

    def retourne_options(self):
        """Retourne les options du tunnel"""
        return (self._source, self._destination)
