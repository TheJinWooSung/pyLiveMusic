class MemoryRoomRepository:

    def __init__(self, rooms):
        self.rooms = rooms

    async def create(self, room_id, name, controllers, viewer_token=None, control_token=None):
        document = {
            "_id": room_id,
            "name": name,
            "controllers": list(controllers),
            "viewer_token": viewer_token,
            "control_token": control_token,
        }

        self.rooms[room_id] = document
        return document

    async def get(self, room_id):
        return self.rooms.get(room_id)

    async def list(self):
        return list(self.rooms.values())

    async def delete(self, room_id):
        self.rooms.pop(room_id, None)

class MemoryUserRepository:

    def __init__(self, users):
        self.users = users

    async def get(self, user_id):
        return self.users.get(user_id)

    async def create(self, user_id, username):
        document = {
            "_id": user_id,
            "username": username
        }

        self.users[user_id] = document

        return document