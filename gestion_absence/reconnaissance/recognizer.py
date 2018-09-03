
# import the necessary packages
from traitement_BD.classes import Collecteur,Writer
from traitement_BD.module import etudiants_CNE
from model.classes import Fiche_absence,Etudiant
from imutils.video import VideoStream
import face_recognition
import datetime
import imutils
import pickle
import time
import cv2


class Recognizer :
    def __init__(self):
        self.collecteur = Collecteur()

    def start(self):
        self.gerer_seances()

    def gerer_seances(self):

        # boucler sur l'ensemble des séances du jour
        for i,seance in enumerate(self.collecteur.seances):
            print("**  séance numéro %d : %s   ==>  %s  **" %(i+1, seance.heure_depart, seance.heure_fin))
            # récuperer les 'nom_prenom' des étudiants présents
            nicknames = self.gerer_seance(seance.heure_depart)
            if nicknames is not None :
                print("[INFO] groupe numero ",seance.groupe_ID)
                print("[INFO] traitement des données en cours ...")
                # récuperer les dictionnaires contenants les étudiants présents et absents
                dict_presents,dict_absents = etudiants_CNE(nicknames,seance.groupe_ID)

                # initialiser la liste des objets de la classe Etudiant
                etudiants_presents = []
                etudiants_absents = []

                # boucler sur les deux dictionnaires
                for CNE,fullName in dict_presents.items() :
                    # créer un objet de la classe Etudiant
                    etudiant = Etudiant(CNE,fullName)
                    etudiants_presents.append(etudiant)
                for CNE,fullName in dict_absents.items() :
                    # créer un objet de la classe Etudiant
                    etudiant = Etudiant(CNE,fullName)
                    etudiants_absents.append(etudiant)

                # initialiser et remplir la fiche d'absence
                fiche = Fiche_absence(seance)
                fiche.ajouter_etudiants(etudiants_presents,True)
                fiche.ajouter_etudiants(etudiants_absents,False)

                # Initialiser le 'Writer'
                writer = Writer(fiche)
                # enregister la fiche d'absence dans la base de données
                writer.enregistrer_fiche()
                print("[INFO] la fiche d'absence est enregistrée.")
            else :
                print("[WARNING] la séance est expirée.")
            print('---------------------------------------------------')

    def gerer_seance(self,heure_depart):
        '''
        cette méthode lance la reconnaissance des étudiants pendant une séance

        :param heure_depart: heure de départ de la séance décalée par 5 min (avant )
        :return: liste des étudiants présents dans la séance
        '''

        # transformer les string en objets de type time
        finish_time = datetime.datetime.strptime(heure_depart, "%H:%M")
        start_time = finish_time - datetime.timedelta(hours=0,minutes=1)
        start_time = start_time.time()
        finish_time = finish_time.time()
        # récuperer le temps réel
        current_time = datetime.datetime.now().time()

        while current_time < start_time :
            # synchroniser le temps réel
            current_time = datetime.datetime.now().time()

        # commencer la reconnaissance des étudiants

        # initialiser la liste des étudiants détectés par le système
        etudiants_presents = None
        # éviter de démarer la caméra si la séance est expirée
        if current_time >= finish_time :
            return etudiants_presents

        # charger les encodages de tous les étudiants
        print("[INFO] loading encodings...")
        data = pickle.loads(open("encodings.pickle", "rb").read())

        # initialiser le video stream et pointer sur la sortie du fichier video, puis
        # permettre la caméra de se réchauffer
        print("[INFO] starting video stream...")
        vs = VideoStream(src=0).start()
        writer = None
        time.sleep(2.0)
        # initialiser l'ensemble des étudiants présents
        etudiants_presents = set()
        # boucler sur des frames du video stream
        while current_time < finish_time :

            # récuperer un frame du video stream
            frame = vs.read()

            # convertir le frame du BGR au RGB puis changer sa taille pour qu'elle devient
            # de 750px en largeur (pour accélerer le processing)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            rgb = imutils.resize(frame, width=750)
            r = frame.shape[1] / float(rgb.shape[1])

            # detecter les coordonnées (x, y)des boxes
            # correspondant à chaque visage dans le frame, puis
            # reconnaître le visage de chaqu'un d'eux
            boxes = face_recognition.face_locations(rgb,
                                                    model="hog")
            encodings = face_recognition.face_encodings(rgb, boxes)
            names = []

            # boucler sur les encodages
            for encoding in encodings:
                # comparer les encodages du visage détecté avec celles
                # des visage déjà connus
                matches = face_recognition.compare_faces(data["encodings"],
                                                         encoding, tolerance=0.5)
                name = "Unknown"

                # vérifier si on a trouvé une similitude
                if True in matches:
                    #trouver les indices de toutes les similitudes trouvées puis
                    # initialiser un dictionnaire pour compter le nombre total
                    # des cas de similitude pour chaque visage
                    matchedIdxs = [i for (i, b) in enumerate(matches) if b]
                    counts = {}

                    # boucler sur les indices de similitude et maintenir un
                    # compteur pour chaque visage reconnu
                    for i in matchedIdxs:
                        name = data["names"][i]
                        counts[name] = counts.get(name, 0) + 1

                    # determiner le visage reconnu avec le grand nombre de
                    # votes
                    name = max(counts, key=counts.get)

                # mise à jour de la liste des noms
                names.append(name)
                # Ajouter l'étudiant détecté à l'ensemble des étudiants
                # reconnus pendant la séance
                if name != "Unknown":
                    etudiants_presents.add(name)

            # boucler sur les visages reconnus dans le frame
            for ((top, right, bottom, left), name) in zip(boxes, names):
                # rescale the face coordinates
                top = int(top * r)
                right = int(right * r)
                bottom = int(bottom * r)
                left = int(left * r)

                # dessiner le nom du visage prédit dans l'image
                cv2.rectangle(frame, (left, top), (right, bottom),
                              (0, 255, 0), 2)
                y = top - 15 if top - 15 > 15 else top + 15
                cv2.putText(frame, name, (left, y), cv2.FONT_HERSHEY_SIMPLEX,
                            0.75, (0, 255, 0), 2)

            # si le 'writer'du video est null  *ET* nous sommes supposés d'écrire
            # la video de sortie dans le disque --> initialiser le 'writer'
            if writer is None and 'output/videooutput.avi' is not None:
                fourcc = cv2.VideoWriter_fourcc(*"MJPG")
                writer = cv2.VideoWriter('output/videooutput.avi', fourcc, 20,
                                         (frame.shape[1], frame.shape[0]), True)

            # si le 'writer'du video est non null, écrire le frame avec
            # les visages reconnus dans le disque
            if writer is not None:
                writer.write(frame)
            # afficher le streaming
            cv2.imshow("Frame", frame)
            key = cv2.waitKey(1) & 0xFF

            # synchroniser le temps réel
            current_time = datetime.datetime.now().time()

        # arrêter le video stream
        cv2.destroyAllWindows()
        vs.stop()

        # check to see if the video writer point needs to be released
        if writer is not None:
            writer.release()
        time.sleep(2.0)
        return etudiants_presents


