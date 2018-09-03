from gestion_absence.reconnaissance.recognizer import Recognizer


if __name__ == '__main__':

    # initialiser le système de gestion d'absence
    systeme_gestion_absence = Recognizer()
    # démarer le système
    systeme_gestion_absence.start()
