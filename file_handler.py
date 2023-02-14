from os import walk
import shutil, os
import time
import magic
import uuid
from datetime import datetime

# Definieren der Magic Datei auslese in einer Variablen
mime = magic.Magic(mime=True)


# Überprüfen der Ordner der neuen und zu bearbeiteten Files
def check_first():
    # Die neuen Files in einem Array speichern
    newfilenames = next(walk('C:/abschluss_projekt/new_bills'), (None, None, []))[2] 
    # Die zu bearbeiteten Files in einem Array speichern
    editfilenames = next(walk('C:/abschluss_projekt/edit_bills'), (None, None, []))[2]
    # Wenn neue Files verfügbar sind und keine Files im edit Ordner sind, True als Wert zurückgeben
    if len(editfilenames) < 1 and len(newfilenames) > 0:
        return True 
    # Sonst False zurückgeben
    return False

# Funktion um eine File vom neuen zum edit Ordner zu verschieben
def move_file_from_new_to_edit():
    newfilenames = next(walk('C:/abschluss_projekt/new_bills'), (None, None, []))[2] 
    editfilenames = next(walk('C:/abschluss_projekt/edit_bills'), (None, None, []))[2] 
    # Kontroll print-statements
    print(f'new file at start:   {newfilenames}')
    print(f'edit file at start:  {editfilenames}')
    # Erneute Überprüfung ob Files im neuen vorhanden bzw im edit nicht vorhanden sind
    if len(editfilenames) < 1:
        if len(newfilenames) > 0:
            # Anlegen einer Unique ID für den Job
            newId = uuid.uuid4()
            # Anlegen einer Textdatei mit dem Namen der Rechnung und der Unique ID. Die Unique ID wird auch noch in die 
            # Text Datei geschrieben und im Edit Ordner abgelegt.
            with open(f'C:/abschluss_projekt/edit_bills/{os.path.splitext(newfilenames[0])[0]}_{newId}.txt', 'w') as file:
                file.write(f'Job ID: {newId} \n')
            # Verschieben der PDF Datei in den Edit Ordner
            shutil.move('C:/abschluss_projekt/new_bills/' + newfilenames[0], 'C:/abschluss_projekt/edit_bills/')


# Die Metadaten der PDF Datei auslesen
def check_file_info():
    # Die Dateien im edit Ordner als Array auslesen
    editfilenames = next(walk('C:/abschluss_projekt/edit_bills'), (None, None, []))[2] 
    # Kontroll-print-statement
    print(f'edit file in work: {editfilenames}')
    # Überprüfen ob Files im edit Ordner vorhanden sind
    if len(editfilenames) > 0:
        # Auslesen/Finden der Text Datei
        for file in os.listdir('C:/abschluss_projekt/edit_bills/'):
            if file.endswith('.txt'):
                # Öffnen der Text Datei die gefunden wurde
                with open(os.path.join('C:/abschluss_projekt/edit_bills/', file), 'a') as f:
                    for pdfFile in os.listdir('C:/abschluss_projekt/edit_bills/'):
                        if pdfFile.endswith('.pdf'):
                            # Den Namen der PDF Datei einfügen
                            f.write(f'File name: {pdfFile} \n')
                            # Den Pfad der PDF Datei definieren
                            file_with_path = f'C:/abschluss_projekt/edit_bills/{pdfFile}'
                            # Die Größe der Datei einfügen
                            f.write(f'File size: {os.path.getsize(file_with_path)} \n')
                            # Datum der Erstellung der PDF Datei einfügen
                            f.write(f'created: {datetime.fromtimestamp(os.path.getctime(file_with_path)).strftime("%Y-%m-%d %H:%M:%S")} \n')
                            # Das DateiFormat (mime) der Datei einfügen
                            f.write(f'Type: {mime.from_file(file_with_path)}')


# Die Dateien vom edit zum finished Ordner verschieben
def move_file_from_edit_to_finished():
    # Die Dateien im edit Ordner als Array auslesen 
    editfilenames = next(walk('C:/abschluss_projekt/edit_bills'), (None, None, []))[2]
    new_id_folder = ''
    # Den Namen der Text Datei im Ordner finden
    for file in os.listdir('C:/abschluss_projekt/edit_bills/'):
        if file.endswith('.txt'):
            # Einen neuen Ordner im finished Ordner anlegen mit dem Namen der text Datei ohne das .txt
            new_id_folder = f'C:/abschluss_projekt/done_bills/{os.path.splitext(file)[0]}'
            os.mkdir(new_id_folder)
    # Die Dateien aus dem edit Ordner in den neuen Ordner verschieben
    for f in editfilenames:
        shutil.move('C:/abschluss_projekt/edit_bills/' + f, new_id_folder)
    # Kontroll-print-statement
    donefilenames = next(walk('C:/abschluss_projekt/done_bills'), (None, None, []))[2]
    print(f'done files: {donefilenames}')


