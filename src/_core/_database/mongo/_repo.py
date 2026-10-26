class MongoRoomRepository:

    def __init__(self, collection):
        self.collection = collection

    async def create(self, room_id, name, controllers, viewer_token=None):
        document = {
            "_id": room_id,
            "name": name,
            "controllers": list(controllers),
            "viewer_token": viewer_token,
        }

        await self.collection.replace_one(
            {"_id": room_id},
            document,
            upsert=True,
        )
        return document

    async def get(self, room_id):
        return await self.collection.find_one({"_id": room_id})

    async def list(self):
        return [document async for document in self.collection.find({})]

    async def delete(self, room_id):
        await self.collection.delete_one({"_id": room_id})


class MongoUserRepository:

    def __init__(self, collection):

        self.collection = collection

    async def get(self, user_id):
        return await self.collection.find_one({"_id": user_id})

    async def create(
        self,
        user_id,
        username,
    ):

        document = {"_id": user_id, "username": username}

        await self.collection.replace_one(
            {"_id": user_id},
            document,
            upsert=True,
        )

        return document