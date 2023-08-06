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

class Terminal:
    """Ouvre un shell sur une machine distante"""

    def __init__(self, opts):
        self.ordres = []
        self.premiereligne = True
        self.commande = False
        self.utilisateurroot = False
        self.destination = ''
        self.machinefinale = ''
        self.extfichier = '.sh'
        self.jetons = {}
        self.indice = 0
        delai = opts.lesoptions()[0].delai
        self.entetel1 = '#!/usr/bin/expect -f\n'
        self.entetel2 = 'set timeout %s\n\n' % str(delai)
        self.script = [self.entetel1, self.entetel2]
        if opts.lesoptions()[0].repsortie is not None:
            self.destination = opts.lesoptions()[0].repsortie + sep
        else:
            self.destination = ''
        self.extrait_ordres(opts.lesoptions()[0].nomfichier)

    def extrait_ordres(self, nomfichier):
        """Extrait les ordres du fichier d'ordres"""
        try:
            if nomfichier is not None:
                self.ordres = open(expanduser(nomfichier), 'r').readlines()
            else:
                self.ordres = sys.stdin.readlines()
        except IOError, message:
            print message
            sys.exit(1)
        except KeyboardInterrupt:
            print "Bélier a été arrêté manuellement par l'utilisateur."
            sys.exit(1)
        for boucle in xrange(2):
            for num in xrange(len(self.ordres)):
                if boucle == 0:
                    if '\0' in self.ordres[num]:
                        print "Format du fichier d'ordres invalide. \
Peut-être un fichier binaire ?"
                        sys.exit(1)
                    self.ordres[num] = self.remplace_guillemets_motdepasse(
                                                            self.ordres[num]) 
                    if len(self.ordres[num].split(' ')) > 5:
                        print "Nombre invalide d'arguments \
sur la ligne du fichier d'ordres"
                        sys.exit(1)
                    identifiant = self.ordres[num].split(' ')[0]
                    if len(identifiant) <= 2 and identifiant != linesep:
                        print "Un nom d'hôte doit contenir au \
moins deux caractères (rfc952)"
                        sys.exit(1)
                    ipoudns = identifiant.split('@')[-1]
                    if len(ipoudns) > 255:
                        print 'La taille de votre nom de domaine \
dépasse 255 caractères'
                        sys.exit(1)
                    for hostname in ipoudns.split('.'):
                        if len(hostname) > 64:
                            print "La taille de votre nom d'hôte \
dépasse 64 caractères"
                            sys.exit(1)
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
                nomjeton = 'jeton%s' % str(self.indice)
                self.jetons[nomjeton] = chaine.strip('"')
                ligne = ligne.replace(chaine, nomjeton, 1)
                self.indice = self.indice + 1
            else:
                temoin = False
        return ligne


    def fin_liste_ordres(self, num):
        """On traite la fin d'une liste d'ordres"""
        if (self.ordres[num] == linesep and self.script[-1] != self.entetel2)\
or (num + 1 == len(self.ordres) and self.script[-1] != self.entetel2):
            if not self.commande:
                self.script.append('interact +++ return\n')
            else:
                self.script.append('expect eof\n')
            resultat = abspath(join(self.destination,
                 ''.join([self.machinefinale, self.extfichier])))
            try:
                open(resultat, 'w').writelines(self.script)
                chmod(resultat, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR )
            except IOError, message:
                print message
                sys.exit(1)
            self.script = [self.entetel1, self.entetel2]
            self.premiereligne = True
            self.commande = False
            self.utilisateurroot = False

    def interprete_ordres(self, num):
        """On interprete un ordre"""
        port = ''
        ligne = self.ordres[num]
        if ligne != linesep:
            if self.commande:
                self.traite_commande(ligne)
            else:
                machine = ligne.split()[0]
                self.machinefinale = ligne.split()[0].split('@')[-1]
                if ':' in self.machinefinale:
                    self.machinefinale, port = self.machinefinale.split(':')
                    machine = ligne.split()[0].split(':')[0]
                if self.premiereligne:
                    if port == '':
                        self.script.append('spawn ssh %s\n' % machine)
                        self.premiereligne = False
                    else:
                        self.script.append('spawn ssh -p %s %s\n' %
                                                 (port, machine))
                        self.premiereligne = False
                else:
                    if port == '':
                        self.script.append('send "ssh %s\\r"\n' % machine)
                    else:
                        self.script.append('send "ssh -p %s %s\\r"\n' %
                                                     (port, machine))
                if ligne.split()[-1] == '-c':
                    self.avec_commande(ligne)
                    self.commande = True
                else:
                    self.sans_commande(ligne)

    def avec_commande(self, ligne):
        """La ligne du fichier d'ordre contient le symbole commande"""
        if len(ligne.split()) == 2:
            self.script.append('expect "$"\n')
        if len(ligne.split()) == 3:
            self.envoie_motdepasse_ssh(ligne.split()[1])
            self.script.append('expect "$"\n')
        if len(ligne.split()) ==  4 :
            self.script.append('expect "$"\n')
            self.change_utilisateur(ligne.split()[1], ligne.split()[2])
        if len(ligne.split()) ==  5 :
            self.envoie_motdepasse_ssh(ligne.split()[1])
            self.script.append('expect "$"\n')
            self.change_utilisateur(ligne.split()[2], ligne.split()[3])

    def sans_commande(self, ligne):
        """La ligne du fichier d'ordre ne contient pas le symbole commande"""
        if len(ligne.split()) == 1:
            self.script.append('expect "$"\n')
        if len(ligne.split()) == 2:
            self.envoie_motdepasse_ssh(ligne.split()[1])
            self.script.append('expect "$"\n')
        if len(ligne.split()) ==  3 :
            self.script.append('expect "$"\n')
            self.change_utilisateur(ligne.split()[1], ligne.split()[2])
        if len(ligne.split()) ==  4 :
            self.envoie_motdepasse_ssh(ligne.split()[1])
            self.script.append('expect "$"\n')
            self.change_utilisateur(ligne.split()[2], ligne.split()[3])

    def traite_commande(self, ligne):
        """Traite la commande contenue dans la ligne courante"""
        self.script.append('send "%s\\r"\n' % ligne.rstrip(linesep))
        self.prepare_prompt()

    def change_utilisateur(self, utilisateur, motdepasse):
        """Génère le script pour changer d'utilisateur"""
        #motdepasse = motdepasse.replace('"','\\"')
        if motdepasse in self.jetons:
            motdepasse = self.jetons[motdepasse]
        self.script.append('send "su - %s\\r"\n' % utilisateur)
        self.script.append('expect "assword:"\n')
        self.script.append('send "%s\\r"\n' % motdepasse)
        if utilisateur == 'root':
            self.utilisateurroot = True
        else:
            self.utilisateurroot = False
        self.prepare_prompt()

    def prepare_prompt(self):
        """Prépare le prompt en fonction de l'identité de l'utilisateur""" 
        if self.utilisateurroot:
            self.script.append('expect "#"\n')
        else:
            self.script.append('expect "$"\n')

    def envoie_motdepasse_ssh(self, motdepasse):
        """Envoie le mot de passe lors d'une connexion ssh"""
        #motdepasse = motdepasse.replace('"','\\"')
        if motdepasse in self.jetons:
            motdepasse = self.jetons[motdepasse]
        self.script.append('expect {\n "assword:" {send "%s\\r"}\n \
"yes/no" {send "yes\\r";exp_continue}\n}\n' % motdepasse)

