from aiohttp import web


async def create_room(request):
    request.app["auth"]._verify(request)
    user_id = request.app["auth"]._get_auth_key()
    data = await request.json()

    name = data.get("name", "Private Room")
    room_id = data.get("room_id")
    rooms = request.app["state"].rooms

    room = await rooms.create(
        name=name,
        controllers={user_id},
        room_id=room_id,
    )

    return web.json_response(room.state(), status=201)


async def get_room(request):
    # Public read is currently required by the built-in browser player,
    # which polls this endpoint without an Authorization header.
    room_id = request.match_info["room_id"]
    room = request.app["state"].rooms.get(room_id)

    if room is None:
        raise web.HTTPNotFound(text="ROOM_NOT_FOUND")

    return web.json_response(room.state())


async def end_room(request):
    request.app["auth"]._verify(request)

    room_id = request.match_info["room_id"]
    rooms = request.app["state"].rooms
    room = rooms.get(room_id)

    if room is None:
        raise web.HTTPNotFound(text="ROOM_NOT_FOUND")

    await rooms.remove(room_id)
    return web.json_response({"status": "ended"})
