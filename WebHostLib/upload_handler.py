from WebHostLib.upload import upload_zip_to_db
from WebHostLib.models import Room, Seed
from uuid import uuid4
import zipfile
import time
import os
from pony.orm import db_session, commit, select

SYSTEM_OWNER = "5501476a-c10f-42e2-9dc6-5e2452e3a0a1"

def handle_new_run(zip_path):
    time.sleep
    with zipfile.ZipFile(zip_path, "r") as zf:
        with db_session:
            seed = upload_zip_to_db(zf, owner=SYSTEM_OWNER)
            if seed:
                room = create_room_for_seed(seed, owner=SYSTEM_OWNER)
                return room

@db_session
def create_room_for_seed(seed, owner):
    room = Room(seed=seed, owner=owner, tracker=uuid4())
    commit()
    print(f"[ROOM_HANDLER] New Room for Seed {seed.id}: Room ID {room.id}")
    return room