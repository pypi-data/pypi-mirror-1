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

#Ouvre un terminal sur une machine distante
"""Ouvre un terminal sur une machine distante"""

import sys
import stat
from os import linesep, chmod, sep
from os.path import expanduser, abspath, join

from optionstunnel import OptionsTunnel

SSHOPTS = '-o NoHostAuthenticationForLocalhost=yes -o StrictHostKeyChecking=no'

class Terminal:
    """Ouvre un shell sur une machine distante"""

    def __init__(self, opts):
        self._ordres = []
        self._est_premiereligne = True
        self._a_commande = False
        self._a_tunnel = False
        self._port = ''
        self._pdest = ''
        self._a_optstunnel = False
        self._dernierssh = 0
        self._destination = ''
        self._machinefinale = ''
        self._extfichier = '.sh'
        self._jetons = {}
        self._indice = 0
        delai = opts.lesoptions()[0].delai
        self._entetel1 = '#!/usr/bin/expect -f%s' % linesep
        self._entetel2 = 'set timeout %s%s%s' % (str(delai), linesep, linesep)
        self._script = [self._entetel1, self._entetel2]
        if opts.lesoptions()[0].repsortie is not None:
            self._destination = opts.lesoptions()[0].repsortie + sep
        else:
            self._destination = ''
        self.extrait_ordres(opts.lesoptions()[0].nomfichier)

    def extrait_ordres(self, nomfichier):
        """Extrait les ordres du fichier d'ordres"""
        # on récupère les ordres (fichiers ou entrée standard)
        try:
            if nomfichier is not None:
                self._ordres = open(expanduser(nomfichier), 'r').readlines()
            else:
                self._ordres = sys.stdin.readlines()
        except IOError, message:
            print message
            sys.exit(1)
        except KeyboardInterrupt:
            print _("Belier has been stopped manually by the user")
            sys.exit(1)
        # deux passes pour étudier les ordres
        for boucle in xrange(2):
            for num in xrange(len(self._ordres)):
                # 1ère passe : on écarte les erreurs banales
                if boucle == 0 and self._ordres[num] != linesep:
                    if '\0' in self._ordres[num]:
                        print _("The file format is invalid \
It may be a binary file ?")
                        sys.exit(1)
                    self._ordres[num] = self.remplace_guillemets_motdepasse(
                                                            self._ordres[num])
                    if len(self._ordres[num].split(' ')) > 5:
                        print _("Incorrect argument number \
on the order file line")
                        sys.exit(1)
                    identifiant = self._ordres[num].split(' ')[0]
                    if len(identifiant) <= 2 and identifiant != linesep:
                        print _("A hostname must contain at \
least two characters (rfc952)")
                        sys.exit(1)
                    ipoudns = identifiant.split('@')[-1]
                    if len(ipoudns) > 255:
                        print _('Your domain name size \
exceeds 255 characters')
                        sys.exit(1)
                    for hostname in ipoudns.split('.'):
                        if len(hostname) > 64:
                            print _("Your hostname size \
exceeds 64 characters")
                            sys.exit(1)
                    if self._ordres[num].split()[-1] == '-c'+ linesep or \
                        self._ordres[num].split()[-1] == '-c':
                        break
                # 2ème passe : on génère les scripts
                if boucle == 1:
                    self.interprete_ordres(num)
                    self.fin_liste_ordres(num)

    def remplace_guillemets_motdepasse(self, ligne):
        """On remplace les mots de passe par un jeton"""
        est_temoin = True
        est_vraiefin = False
        motdepasse = '"'
        # on transforme les mots de passe entre guillemets en jeton
        # on évite ainsi les caractères d'espacement gênants
        while est_temoin:
            debut = ligne.find(' "')
            if debut != -1:
                intermediaire = ligne[debut+2:]
                while not est_vraiefin:
                    if '"' in intermediaire:
                        prochain = intermediaire.find('"')
                        motdepasse = motdepasse + intermediaire[:prochain+1]
                        if motdepasse[-2] == '\\':
                            intermediaire = intermediaire[prochain+1:]
                        else:
                            est_vraiefin = True
                    else:
                        est_vraiefin = True
                chaine = motdepasse
                motdepasse = '"'
                est_vraiefin = False
                nomjeton = 'jeton%s' % str(self._indice)
                self._jetons[nomjeton] = chaine.strip('"')
                ligne = ligne.replace(chaine, nomjeton, 1)
                self._indice = self._indice + 1
            else:
                est_temoin = False
        return ligne

    def fin_liste_ordres(self, num):
        """On traite la fin d'une liste d'ordres"""
        if (self._ordres[num] == linesep and
            self._script[-1] != self._entetel2) or (
                    num + 1 == len(self._ordres) and
                self._script[-1] != self._entetel2):
            # remplace les numéros de port du tunnel
            if self._a_tunnel:
                if self._pdest:
                    if self._port:
                        self._script[self._dernierssh] = self._script[
                            self._dernierssh].replace(
                                '-L9999:127.0.0.1:9999','-L%s:127.0.0.1:%s' % (
                                    self._pdest, self._port),1)
                    else:
                        self._script[self._dernierssh] = self._script[
                            self._dernierssh].replace(
                                '-L9999:127.0.0.1:9999','-L%s:127.0.0.1:22' % (
                                    self._pdest),1)
                else:
                    if self._port:
                        self._script[self._dernierssh] = self._script[
                            self._dernierssh].replace(
                                '127.0.0.1:9999','127.0.0.1:%s'% self._port, 1)
                    else:
                        self._script[self._dernierssh] = self._script[
                            self._dernierssh].replace(
                                '127.0.0.1:9999','127.0.0.1:22', 1)
            # dernière ligne du script en fonction mode commande
            if not self._a_commande:
                self._script.append('interact +++ return%s' % linesep)
            else:
                self._script.append('expect eof%s' % linesep)
            resultat = abspath(join(self._destination,
                 ''.join([self._machinefinale, self._extfichier])))
            # écriture du script
            try:
                open(resultat, 'w').writelines(self._script)
                chmod(resultat, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR )
            except IOError, message:
                print message
                sys.exit(1)
            # compteur à zéro pour le prochain bloc d'ordres
            self._script = [self._entetel1, self._entetel2]
            self._est_premiereligne = True
            self._a_commande = False

    def interprete_ordres(self, num):
        """On interprete un ordre"""
        psource = ''
        pdestination = ''
        ligne = self._ordres[num]
        if ligne != linesep:
            if self._a_commande:
                # on traite le cas spécial du mode commande
                self.traite_commande(ligne)
            elif self._a_optstunnel:
                # on prepare les options du tunnel
                optstunnel = OptionsTunnel(ligne)
                psource, pdestination = \
                    optstunnel.retourne_options()
                nligne = '-L%s:127.0.0.1:%s' % (psource,
                    pdestination)
                self._pdest = pdestination
                self._script[self._dernierssh] = self._script[
                    self._dernierssh].replace(
                        '-L9999:127.0.0.1:9999', nligne)
                self._a_optstunnel = False
            else:
                if ligne.split()[-1] == '-t':
                    self._a_tunnel = True
                if ligne.split()[-1] == '-ot':
                    self._a_tunnel = True
                    self._a_optstunnel = True
                machine = ligne.split()[0]
                self._machinefinale = ligne.split()[0].split('@')[-1]
                self._port = ''
                if ':' in self._machinefinale:
                    self._machinefinale, self._port = \
self._machinefinale.split(':')
                    machine = ligne.split()[0].split(':')[0]
                if self._a_tunnel:
                    tunnelopts = '-L9999:127.0.0.1:9999'
                else:
                    tunnelopts = ''

                if self._est_premiereligne:
                    # première connexion
                    if not self._port:
                        self._script.append('spawn ssh %s %s %s%s' % (
                            SSHOPTS, tunnelopts, machine, linesep))
                    else:
                        self._script.append('spawn ssh -p %s %s %s %s%s' %
                            (self._port, SSHOPTS, tunnelopts, machine, linesep))
                    self._est_premiereligne = False
                else:
                    if not self._port:
                        self._script.append('send -- "ssh %s %s %s\\r"%s' %
                            (SSHOPTS, tunnelopts, machine, linesep))
                    else:
                        self._script.append(
                            'send -- "ssh -p %s %s %s %s\\r"%s' %
                            (self._port, SSHOPTS, tunnelopts, machine,
                                linesep))
                if self._a_tunnel:
                    self._dernierssh = len(self._script) - 1
                if ligne.split()[-1] == '-c':
                    self.avec_commande(ligne)
                    self._a_commande = True
                elif ligne.split()[-1] == '-t' or ligne.split()[-1] == '-ot':
                    self.avec_commande(ligne)
                else:
                    self.sans_commande(ligne)

    def avec_commande(self, ligne):
        """La ligne du fichier d'ordre contient le symbole commande"""
        if len(ligne.split()) == 2:
            self.prepare_prompt()
        if len(ligne.split()) == 3:
            self.envoie_motdepasse_ssh(ligne.split()[1])
        if len(ligne.split()) ==  4 :
            self.prepare_prompt()
            self.change_utilisateur(ligne.split()[1], ligne.split()[2])
        if len(ligne.split()) ==  5 :
            self.envoie_motdepasse_ssh(ligne.split()[1])
            self.change_utilisateur(ligne.split()[2], ligne.split()[3])

    def sans_commande(self, ligne):
        """La ligne du fichier d'ordre ne contient pas le symbole commande"""
        if len(ligne.split()) == 1:
            self.prepare_prompt()
        if len(ligne.split()) == 2:
            self.envoie_motdepasse_ssh(ligne.split()[1])
        if len(ligne.split()) ==  3 :
            self.prepare_prompt()
            self.change_utilisateur(ligne.split()[1], ligne.split()[2])
        if len(ligne.split()) ==  4 :
            self.envoie_motdepasse_ssh(ligne.split()[1])
            self.change_utilisateur(ligne.split()[2], ligne.split()[3])

    def traite_commande(self, ligne):
        """Traite la commande contenue dans la ligne courante"""
        self._script.append('send -- "%s\\r"%s'
            % (ligne.rstrip(linesep), linesep))
        self.prepare_prompt()

    def change_utilisateur(self, utilisateur, motdepasse):
        """Génère le script pour changer d'utilisateur"""
        if motdepasse in self._jetons:
            motdepasse = self._jetons[motdepasse]
        self._script.append('send -- "su - %s\\r"%s' % (utilisateur, linesep))
        self._script.append('expect ":"%s' % linesep)
        self._script.append('send -- "%s\\r"%s' % (motdepasse, linesep))
        self.prepare_prompt()

    def prepare_prompt(self):
        """Prépare le prompt en fonction de l'identité de l'utilisateur"""
        self._script.append('expect -re  "(%s|#|\\\\$) $"%s' % ('%', linesep))

    def envoie_motdepasse_ssh(self, motdepasse):
        """Envoie le mot de passe lors d'une connexion ssh"""
        if motdepasse in self._jetons:
            motdepasse = self._jetons[motdepasse]
        self._script.append('expect -re {@[^\\n]*:}%s' % linesep)
        self._script.append('send -- "%s\\r"%s' % (motdepasse, linesep))
        self.prepare_prompt()
