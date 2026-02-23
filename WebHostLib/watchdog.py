import os
import time
from pathlib import Path
from WebHostLib.upload_handler import handle_new_run_folder, handle_run_folder_deleted
from .models import Room

class WebHostEventHandler(FileSystemEventHandler):
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
        self.observer = Observer()

    def start(self):
        handler = WebHostEventHandler(self.path)
        print(f"[WATCHDOG] Now Observing: {self.path}")
        while True:
            print(f"[WATCHDOG] Still Observing: {self.path}")
            time.sleep(10)

    def stop(self):
        if self.observer.is_alive():
            self.observer.stop()
            self.observer.join()
            print("[WATCHDOG] stopped")

#Watchdog Logik
#   1. Schaue alle 10 Sekunden in welchen Unterordnern von /game sich game-zips befinden
#   2. Ließ Namen der .zip, den Namen des Unterordners, den Inhalt von config.json aus (inkl. der Room und Seed-IDs)
#   3. Berichte den aktuellen Zustand an eine Neue Klasse, die Untersucht, ob in diesen Daten ein Unterschied festzustellen ist
#       3.1. Falls es einen Ordner gibt, dessen Daten noch keine Room-ID hat...
#           3.1.1 ...Kreiere einen neuen Raum
#           3.1.2 ...Schreibe die ID des neuen Raums in die config.json
#       3.2. Falls eine Room-ID aus dem Bericht verschwunden ist, schließe den betroffenen Raum