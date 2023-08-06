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

# Voir la Licence Publique Générale GNU pour plus de détails. Vous devriez
# avoir reçu un exemplaire de la Licence Publique Générale GNU avec ce
# programme ; si ce n'est pas le cas, écrivez à la Free Software Foundation
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.


from distutils.core import setup

setup (name = 'belier',
       version = '0.5',
       description = 'Ouvrir un terminal ou lancer un script via ssh \
a travers plusieurs serveurs intermediaires',
       author = 'Carl Chenet',
       author_email = 'carl.chenet@ohmytux.com',
       url = 'http://www.ohmytux.com/belier',
       packages = ['belier'],
       scripts = ['bel']
)

