class Etudiant:
    '''
    cette classe constitue le modèle d'un étudiant avec tous ses attributs
    '''
    def __init__(self,cne,fullName):
        self.CNE = cne
        sp = fullName.split(' ')
        self.prenom = sp[0]
        self.nom = sp[1]





class Groupe:
    '''
        chaque filière est divisée en groupes d'étudiants, et
        cette classe constitue le modèle d'un groupe d'étudiant avec tous ses attributs
    '''
    def __init__(self,nom, niveau, filiere):
        self.nom = nom
        self.niveau = niveau
        self.filere = filiere


class Seance:
    '''
        cette classe constitue le modèle d'une séance de cours ou examen  avec tous ses attributs
    '''
    def __init__(self,data):
        self.id = data[0]
        self.jour = data[1]
        self.heure_depart = data[2]
        self.heure_fin = data[3]
        self.salle = data[4]
        self.type = data[5]  # le type soit cours, ou examen
        self.groupe_ID = data[6]


class Fiche_absence:
    '''
        cette classe constitue le modèle d'une fiche d'absence
    '''
    def __init__(self,seance):
        self.seance = seance
        self.etudiants_CNE = []
        self.etats_absence = []
    def ajouter_etudiants(self,etudiants,presence):
        # boucler sur les étudiants( objets de la classe Etudiant )
        for etudiant in etudiants :
            self.etudiants_CNE.append(etudiant.CNE)
            self.etats_absence.append(presence)

