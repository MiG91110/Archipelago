import os
from pathlib import Path
from WebHostLib.upload_handler import handle_new_run_folder
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

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


class FolderWatchdog:
    def __init__(self, path="/game"):
        self.path = os.path.abspath(path)
        Path(self.path).mkdir(parents=True, exist_ok=True)
        self.observer = Observer()

    def start(self):
        handler = WebHostEventHandler(self.path)
        self.observer.schedule(handler, self.path, recursive=True)
        self.observer.start()
        print(f"[WATCHDOG] Now Observing: {self.path}")

    def stop(self):
        if self.observer.is_alive():
            self.observer.stop()
            self.observer.join()
            print("[WATCHDOG] stopped")
