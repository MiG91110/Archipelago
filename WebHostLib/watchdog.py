import os
import time
import json
from pathlib import Path
from WebHostLib.upload_handler import handle_new_run
from WebHostLib.autolauncher import cleanup
from .models import Room
from pony.orm import db_session, commit, select


class FolderWatchdog:
    def __init__(self, path="/game"):
        self.path = os.path.abspath(path)
        Path(self.path).mkdir(parents=True, exist_ok=True)

    def start(self):
        print(f"[WATCHDOG] Now Observing: {self.path}")
        while True:
            print(f"[WATCHDOG] Still Observing: {self.path}")
            
            #Check if there are Directories with Runs, which need to be started
            run_dirs: Path[str] = os.listdir(self.path)
            for run_dir in run_dirs:
                print(f"[UPLOAD HANDLER] I found this cool Run: {run_dir}")
                run_dir_fullpath = os.path.join(self.path, run_dir)
                zip_path = None
                for filename in os.listdir(run_dir_fullpath):
                    if filename.lower().endswith(".zip"):
                        zip_path = os.path.join(run_dir_fullpath, filename)
                if zip_path is None:
                    print(f"[UPLOAD HANDLER] But it has no .zip file in it.")
                    continue
                print(f"It has this awesome zip in it: {zip_path}")
                for filename in os.listdir(run_dir_fullpath):
                    if filename.lower() == ("config.json"):
                        config_path = os.path.join(run_dir_fullpath, "config.json")
                        print(f"It also has a config.json named: {config_path}")
                        with open(config_path, 'r') as file:
                            config = json.load(file)
                        room_id = config.get('Room_ID')
                        if room_id is not None:
                            print(f"it even has a Room_ID in it: {room_id}. No Action needed")
                        else:
                            print("But it has no Room_ID. Let's create a room.")
                            room_id = handle_new_run(zip_path).id
                            config['Room_ID'] = str(room_id)
                        with open((config_path), 'w') as file:
                            json.dump(config, file, indent=4)
                
            #Set rooms which have no corresponding run directory to ownerless
            with db_session:
                rooms = select(room for room in Room)
                for room in rooms:
                    print (f"[UPLOAD HANDLER] Found this room: {room.id}")
                    print (f"[UPLOAD HANDLER] Now checking if Room id is obsolete")
                    room_obsolete = True
                    for run_dir in run_dirs:
                        config_path = os.path.join(self.path, run_dir, "config.json")
                        if not os.path.isfile(config_path):
                            continue
                        with open(config_path, 'r') as file:
                            config = json.load(file)
                        if config.get('Room_ID') == str(room.id):
                            room_obsolete = False
                    if room_obsolete:
                        print(f"No corresponding id found in config.json. Now closing Room")
                        room.owner = 0
                        cleanup()
            time.sleep(10)

    def stop(self):
        if self.observer.is_alive():
            self.observer.stop()
            self.observer.join()
            print("[WATCHDOG] stopped")
#Watchdog Logik
#   1. Schaue alle 10 Sekunden in welchen Unterordnern von /game sich game-zips befinden
#   2. Ließ Namen der .zip, den Namen des Unterordners, den Inhalt von config.json aus (inkl. der Room-ID)
#   3. Berichte den aktuellen Zustand an eine Neue Klasse, die Untersucht, ob in diesen Daten ein Unterschied festzustellen ist
#       3.1. Falls es einen Ordner gibt, dessen Daten noch keine Room-ID hat...
#           3.1.1 ...Kreiere einen neuen Raum
#           3.1.2 ...Schreibe die ID des neuen Raums in die config.json
#       3.2. Falls eine Room-ID aus dem Bericht verschwunden ist, schließe den betroffenen Raum