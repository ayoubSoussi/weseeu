import MySQLdb
import datetime
from model.classes import Seance,Fiche_absence
from traitement_BD.module import getKey
import json



class Collecteur:
    '''
    cette classe est un collecteur des données des séances planifiées dans le jour en cours
    '''
    def __init__(self):
        self.seances = []
        # recuperer la date du jour
        now = datetime.datetime.now()
        jour = now.strftime("%d-%m-%Y")
        self.collecter_seances(jour)

    def collecter_seances(self,jour):
        # ouvrir une connexion avec la base de données
        bd = MySQLdb.connect(host='localhost', user='root', passwd='root', db='weseeu')
        c = bd.cursor()
        # extraire les seances plannifies dans le jour en cours
        c.execute("""SELECT * from seance where jour = %s AND salle = %s ; """,(jour,'C14',))
        data = c.fetchall()
        # fermer la connexion
        bd.close()

        # trier la liste des données par ordre chronologique
        liste_triee = self.trier_seances(data)
        # creer la liste des seances (objets ) pour qu'ils soient prêts pour l'utilisation
        self.creer_seances(liste_triee)

    def trier_seances(self,data):
        '''
        cette méthode trie la liste des données des séances par ordre chronologique
        :param data:
        :return liste triée des données:
        '''
        return sorted(data,key=getKey)
    def creer_seances(self,liste):
        '''
        cette méthode crée une liste des objets Seance à partir de la liste des données

        :param liste:
        :return:
        '''
        # vider la liste des objets seances avant de la remplir
        self.seances.clear()
        for seance_donnes in liste:
            seance = Seance(seance_donnes)
            self.seances.append(seance)




class Writer:
    '''
    cette classe enregistre les fiches d'absence dans la base de données
    '''
    def __init__(self,fiche_absence):
        self.fiche_absence = fiche_absence
        # creer un dictionnaire pour stocker l'état d'absence de chaque étudiant
        self.data = dict()

        # stocker les données de la forme { 'etudiant_id' : 'etat_absence' }
        for etudiant_id,etat_absence in zip(self.fiche_absence.etudiants_CNE,self.fiche_absence.etats_absence):
            self.data[etudiant_id] = etat_absence


    def enregistrer_fiche(self):
        # ouvrir une connexion avec la base de données
        bd = MySQLdb.connect(host='localhost', user='root', passwd='root', db='weseeu')
        c = bd.cursor()

        # convertir les données (dictionnaire) en un fichier JSON
        myJson = json.dumps(self.data, ensure_ascii=False)
        # enregistrer le fichier JSON dans la base de données
        c.execute("""INSERT INTO ficheAbsence(seance_ID,fiche) values(%s,%s); """,(self.fiche_absence.seance.id,myJson))

        # valider les modifications
        bd.commit()
        bd.close()


