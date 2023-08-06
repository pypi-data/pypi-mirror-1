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
import os.path

CLASSIFIERS = [
    'Intended Audience :: System Administrators',
    'Development Status :: 4 - Beta',
    'Environment :: Console',
    'License :: OSI Approved :: GNU General Public License (GPL)',
    'Operating System :: OS Independent',
    'Natural Language :: French',
    'Programming Language :: Python',
]



setup(name = 'belier',
    version = '1.0',
    license = 'GNU GPL v3',
    description = 'Ssh connection generation tool',
    long_description = 'Belier allows automated openings of a shell or command executions on remote computers through ssh. The main feature is Belier\'s ability to cross several computers before joining the final machine.',
    classifiers = CLASSIFIERS,
    author = 'Carl Chenet',
    author_email = 'chaica@ohmytux.com',
    url = 'http://www.ohmytux.com/belier',
    download_url = 'http://www.ohmytux.com/belier',
    packages = ['belier'],
    scripts = ['bel'],
    data_files=[(os.path.join('share','locale','fr','LC_MESSAGES'), ['i18n/fr/bel.mo'])]
)

