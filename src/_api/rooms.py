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

    result = room.state()
    result["player_token"] = room.viewer_token
    result["control_token"] = room.control_token
    result["player_path"] = f"/room/{room.id}#{room.viewer_token}"
    return web.json_response(result, status=201)


async def get_room(request):
    room_id = request.match_info["room_id"]
    room = request.app["state"].rooms.get(room_id)

    if room is None:
        raise web.HTTPNotFound(text="ROOM_NOT_FOUND")

    request.app["auth"]._verify_room_access(request, room)
    return web.json_response(room.state())


async def end_room(request):
    room_id = request.match_info["room_id"]
    rooms = request.app["state"].rooms
    room = rooms.get(room_id)

    if room is None:
        raise web.HTTPNotFound(text="ROOM_NOT_FOUND")

    request.app["auth"]._verify_room_control(request, room)
    await rooms.remove(room_id)
    return web.json_response({"status": "ended"})
