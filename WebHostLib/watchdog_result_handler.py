import zipfile
import time
from uuid import UUID, uuid4
from pony.orm import db_session, commit
from WebHostLib.upload import upload_zip_to_db
from WebHostLib.models import Room, Command
from WebHostLib.autolauncher import cleanup

#TODO: This is a very hacky way to handle runs that are started outside of the webhost, but it works for now. Maybe we can find a better way to do this in the future.
SYSTEM_OWNER = "5501476a-c10f-42e2-9dc6-5e2452e3a0a1"

def handle_new_run(zip_path, port):
    time.sleep
    with zipfile.ZipFile(zip_path, "r") as zf:
        with db_session:
            seed = upload_zip_to_db(zf, owner=SYSTEM_OWNER)
            if seed:
                room = create_room_for_seed(seed, owner=SYSTEM_OWNER, port=port)
                return room

def handle_obsolete_room(room):
    with db_session:
            print(f"[WATCHDOG] No corresponding id found in config.json. Now closing Room")
            Command(room=room, commandtext="/exit")
            commit()
            time.sleep(5)
            room.owner = UUID(int=0)
            cleanup()

@db_session
def create_room_for_seed(seed, owner, port):
    #TODO: Let the folder watchdog report if there is a port determined for the run, and use that port instead of the default one.
    room = Room(seed=seed, owner=owner, tracker=uuid4(),last_port=port)
    commit()
    print(f"[ROOM_HANDLER] New Room for Seed {seed.id}: Room ID {room.id}")
    return room