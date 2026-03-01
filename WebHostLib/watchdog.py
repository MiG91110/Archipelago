import os
import time
import json
from pathlib import Path
from pony.orm import db_session, select
from WebHostLib.watchdog_result_handler import handle_new_run, handle_obsolete_room
from .models import Room


class Watchdog:
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
                print(f"[WATCHDOG] I found this Run: {run_dir}")
                run_dir_fullpath = os.path.join(self.path, run_dir)
                zip_path = None
                for filename in os.listdir(run_dir_fullpath):
                    if filename.lower().endswith(".zip"):
                        zip_path = os.path.join(run_dir_fullpath, filename)
                if zip_path is None:
                    print(f"[WATCHDOG] But it has no zip file in it.")
                    continue
                print(f"[WATCHDOG] It has this zip in it: {zip_path}")
                for filename in os.listdir(run_dir_fullpath):
                    if filename.lower() == ("config.json"):
                        config_path = os.path.join(run_dir_fullpath, "config.json")
                        print(f"[WATCHDOG] It has a config.json named: {config_path}")
                        with open(config_path, 'r') as file:
                            config = json.load(file)
                        room_id = config.get('Room_ID')
                        if room_id is None:
                            print("[WATCHDOG] It has no Room_ID. Now creating room.")
                            port = self.find_port_for_run(run_dir)
                            room_id = handle_new_run(zip_path, port).id
                            config['Room_ID'] = str(room_id)
                        with open((config_path), 'w') as file:
                            json.dump(config, file, indent=4)
                
            #Set rooms which have no corresponding run directory to ownerless
            with db_session:
                rooms = select(room for room in Room)
                for room in rooms:
                    print (f"[WATCHDOG] Found this room: {room.id}")
                    print (f"[WATCHDOG] Now checking if Room id is obsolete")
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
                        handle_obsolete_room(room)
            time.sleep(10)
        
    def find_port_for_run(self, run_dir):
        port_in_dirname = run_dir[-5:]
        if port_in_dirname is not None and port_in_dirname.isdigit():
            return int(port_in_dirname)
        return None