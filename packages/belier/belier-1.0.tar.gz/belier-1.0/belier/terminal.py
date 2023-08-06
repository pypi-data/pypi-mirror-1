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

#Ouvre un terminal sur une machine distante
"""Ouvre un terminal sur une machine distante"""

import sys
import stat
from os import linesep, chmod, sep
from os.path import expanduser, abspath, join

SSHOPTS = '-o NoHostAuthenticationForLocalhost=yes -o StrictHostKeyChecking=no'

class Terminal:
    """Ouvre un shell sur une machine distante"""

    def __init__(self, opts):
        self._ordres = []
        self._premiereligne = True
        self._commande = False
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
        for boucle in xrange(2):
            for num in xrange(len(self._ordres)):
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
                    if self._ordres[num].split()[-1] == '-c'+linesep or \
                        self._ordres[num].split()[-1] == '-c':
                        break 

                if boucle == 1:
                    self.interprete_ordres(num)
                    self.fin_liste_ordres(num)

    def remplace_guillemets_motdepasse(self, ligne):
        """On remplace les mots de passe par un jeton"""
        temoin = True
        vraiefin = False
        motdepasse = '"'
        while temoin:
            debut = ligne.find(' "')
            if debut != -1:
                intermediaire = ligne[debut+2:]
                #while vraiefin == False:
                while not vraiefin: 
                    if '"' in intermediaire:
                        prochain = intermediaire.find('"')
                        motdepasse = motdepasse + intermediaire[:prochain+1]
                        if motdepasse[-2] == '\\':
                            intermediaire = intermediaire[prochain+1:]
                        else:
                            vraiefin = True
                    else:
                        vraiefin = True
                chaine = motdepasse
                motdepasse = '"'
                vraiefin = False
                nomjeton = 'jeton%s' % str(self._indice)
                self._jetons[nomjeton] = chaine.strip('"')
                ligne = ligne.replace(chaine, nomjeton, 1)
                self._indice = self._indice + 1
            else:
                temoin = False
        return ligne


    def fin_liste_ordres(self, num):
        """On traite la fin d'une liste d'ordres"""
        if (self._ordres[num] == linesep and 
			self._script[-1] != self._entetel2) or (num + 1 == len(self._ordres) and 
				self._script[-1] != self._entetel2):
            if not self._commande:
                self._script.append('interact +++ return%s' % linesep)
            else:
                self._script.append('expect eof%s' % linesep)
            resultat = abspath(join(self._destination,
                 ''.join([self._machinefinale, self._extfichier])))
            try:
                open(resultat, 'w').writelines(self._script)
                chmod(resultat, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR )
            except IOError, message:
                print message
                sys.exit(1)
            self._script = [self._entetel1, self._entetel2]
            self._premiereligne = True
            self._commande = False

    def interprete_ordres(self, num):
        """On interprete un ordre"""
        port = ''
        ligne = self._ordres[num]
        if ligne != linesep:
            if self._commande:
                self.traite_commande(ligne)
            else:
                machine = ligne.split()[0]
                self._machinefinale = ligne.split()[0].split('@')[-1]
                if ':' in self._machinefinale:
                    self._machinefinale, port = self._machinefinale.split(':')
                    machine = ligne.split()[0].split(':')[0]
                if self._premiereligne:
                    if not port:
                        self._script.append('spawn ssh %s %s%s' % (SSHOPTS, machine, linesep))
                        self._premiereligne = False
                    else:
                        self._script.append('spawn ssh -p %s %s %s%s' %
                                                 (port, SSHOPTS, machine, linesep))
                        self._premiereligne = False
                else:
                    if not port:
                        self._script.append('send -- "ssh %s %s\\r"%s' % 
                                            (SSHOPTS, machine, linesep))
                    else:
                        self._script.append('send -- "ssh -p %s %s %s\\r"%s' %
                                                     (port, SSHOPTS, machine, linesep))
                if ligne.split()[-1] == '-c':
                    self.avec_commande(ligne)
                    self._commande = True,
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
        self._script.append('send -- "%s\\r"%s' % (ligne.rstrip(linesep), linesep))
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
        
