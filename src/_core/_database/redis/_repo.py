import json


class RedisRoomRepository:

    def __init__(self, redis, key_prefix="pylivemusic"):
        self.redis = redis
        self.key_prefix = key_prefix
        self.rooms_key = f"{key_prefix}:rooms"

    def _room_key(self, room_id):
        return f"{self.rooms_key}:{room_id}"

    async def create(self, room_id, name, controllers, viewer_token=None):

        document = {
            "_id": room_id,
            "name": name,
            "controllers": list(controllers),
            "viewer_token": viewer_token,
        }

        await self.redis.set(
            self._room_key(room_id),
            json.dumps(document),
        )

        return document

    async def get(self, room_id):

        data = await self.redis.get(
            self._room_key(room_id)
        )

        if data is None:
            return None

        return json.loads(data)

    async def list(self):

        documents = []

        async for key in self.redis.scan_iter(
            match=f"{self.rooms_key}:*"
        ):
            data = await self.redis.get(key)

            if data is not None:
                documents.append(json.loads(data))

        return documents

    async def delete(self, room_id):

        await self.redis.delete(
            self._room_key(room_id)
        )


class RedisUserRepository:

    def __init__(self, redis, key_prefix="pylivemusic"):
        self.redis = redis
        self.key_prefix = key_prefix
        self.users_key = f"{key_prefix}:users"

    def _user_key(self, user_id):
        return f"{self.users_key}:{user_id}"

    async def get(self, user_id):

        data = await self.redis.get(
            self._user_key(user_id)
        )

        if data is None:
            return None

        return json.loads(data)

    async def create(
        self,
        user_id,
        username,
    ):

        document = {
            "_id": user_id,
            "username": username,
        }

        await self.redis.set(
            self._user_key(user_id),
            json.dumps(document),
        )

        return document