import MySQLdb



def getKey(item):
    # item[2] dessine l'heure de départ de chaque séance
    return item[2]

def etudiants_CNE(nicknames,groupe_ID):
    '''
    cette méthode récupère les CNE des étudiants présents et absents de la base de données

    :param nicknames: des chaînes de caractères de la forme "nom_prénom"
    :return: les CNE de l'étudiant présents et absents
    '''
    # initialiser les listes des noms et prénom
    noms = []
    prenoms = []
    etudiants_presents = dict()
    etudiants_absents = dict()
    if len(nicknames) <= 0:
        noms.append("rien")
        prenoms.append("rien")
    # boucler sur l'ensembles des nicknames
    for nickname in nicknames :
        # séparer les noms et prénoms des étudiants à partir
        # des chaînes de caractères 'nom_prenom'
        result = nickname.split("_")
        noms.append(result[1])
        prenoms.append(result[0])

    # ouvrir une connexion avec la base de données
    bd = MySQLdb.connect(host='localhost', user='root', passwd='root', db='weseeu')
    c = bd.cursor()
    c.execute("""SELECT CNE,prenom,nom FROM etudiant where (nom IN %s AND prenom IN %s ) AND groupe_ID = %s""",(tuple(noms),tuple(prenoms),groupe_ID))

    # récuperer les CNEs des étudiants présents
    fetch = c.fetchall()
    if len(fetch) > 0:
        for item in fetch:
            etudiants_presents.update({item[0] : item[1]+' '+item[2] })


    # récuperer les CNEs des étudiants absents
    c.execute("""SELECT CNE,prenom,nom FROM etudiant where (nom NOT IN %s AND prenom NOT IN %s ) AND groupe_ID = %s""",(tuple(noms),tuple(prenoms),groupe_ID))
    fetch = c.fetchall()
    if len(fetch) > 0:
        for item in fetch:
            etudiants_absents.update({item[0] : item[1]+' '+item[2]})

    # fermer la connexion avec la base de données
    bd.close()

    return etudiants_presents,etudiants_absents

