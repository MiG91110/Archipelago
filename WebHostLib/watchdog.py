import os
import time
import json
from pathlib import Path
from WebHostLib.upload_handler import handle_new_run_folder, handle_run_folder_deleted
from .models import Room
from pony.orm import db_session, commit, select

class WebHostEventHandler():
    def __init__(self, base_path):
        self.base_path = os.path.abspath(base_path)

    def _is_direct_child(self, path):
        path = os.path.abspath(path)
        parent = os.path.dirname(path)
        return parent == self.base_path
    
    def on_modified(self, event):
        if not event.is_directory:
            return
        if event.src_path == self.base_path:
            return    
        print(f"[WATCHDOG] File changed: {event.src_path}")

    def on_created(self, event):
        if not event.is_directory:
            return
        if not self._is_direct_child(event.src_path):
            return
        print(f"[WATCHDOG] File created: {event.src_path}")
        handle_new_run_folder(event.src_path)

    def on_deleted(self, event):
        if not event.is_directory:
            return
        if not self._is_direct_child(event.src_path):
            return
        print(f"[WATCHDOG] File deleted: {event.src_path}")
        handle_run_folder_deleted(event.src_path)


class FolderWatchdog:
    def __init__(self, path="/game"):
        self.path = os.path.abspath(path)
        Path(self.path).mkdir(parents=True, exist_ok=True)

    def start(self):
        handler = WebHostEventHandler(self.path)
        print(f"[WATCHDOG] Now Observing: {self.path}")
        #while True:
        print(f"[WATCHDOG] Still Observing: {self.path}")
        
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
                        print(f"it even has a Room_ID in it: {room_id}")
                    else:
                        print("But it has no Room_ID. Let me add one")
                        config['Room_ID'] = "RAUM JOONGE"
                    with open((config_path), 'w') as file:
                        json.dump(config, file, indent=4)
            
        with db_session:
            rooms = select(room for room in Room)
            for room in rooms:
                print (f"[UPLOAD HANDLER] Found this room: {room.id}")
                if room.zip_name:
                    print (f"[UPLOAD HANDLER] It has the zip_name: {room.zip_name}")
                else:
                    print(f"[UPLOAD HANDLER] The zip_name is not set.")
                if room.dir_path:
                    print (f"[UPLOAD HANDLER] It has the dir_path: {room.dir_path}")
                else:
                    print(f"[UPLOAD HANDLER] The dir_path is not set.")
                # room.owner = 0
                # print (f"[UPLOAD HANDLER] ID of room {room.id} is now {room.owner}")
        # time.sleep(10)

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