from aiohttp import web


def get_room_for_control(request):
    room = request.app["state"].rooms.get(request.match_info["room_id"])
    if room is None:
        raise web.HTTPNotFound(text="ROOM_NOT_FOUND")

    request.app["auth"]._verify_room_control(request, room)
    return room


async def get_queue(request):
    room = get_room_for_control(request)

    return web.json_response({
        "room_id": room.id,
        "current": (
            {"id": room.current.id, "title": room.current.title}
            if room.current else None
        ),
        "queue": [
            {"id": item.id, "title": item.title}
            for item in room.queue
        ],
    })


async def add_track(request):
    room = get_room_for_control(request)

    data = await request.json()
    if not isinstance(data, dict):
        raise web.HTTPBadRequest(text="Expected a JSON object")

    title = data.get("title")
    path = data.get("path")
    if not isinstance(title, str) or not title.strip():
        raise web.HTTPBadRequest(text="INVALID_TRACK_TITLE")
    if not isinstance(path, str) or not path.strip():
        raise web.HTTPBadRequest(text="INVALID_TRACK_PATH")

    item = await room.add_track(title=title.strip(), path=path.strip())
    return web.json_response(
        {"id": item.id, "title": item.title},
        status=201,
    )


async def remove_track(request):
    room = get_room_for_control(request)

    track_id = request.match_info["track_id"]
    async with room.lock:
        before = len(room.queue)
        room.queue = [item for item in room.queue if item.id != track_id]
        if len(room.queue) == before:
            raise web.HTTPNotFound(text="TRACK_NOT_FOUND")

    return web.json_response({
        "queue": [{"id": item.id, "title": item.title} for item in room.queue]
    })


async def clear_queue(request):
    room = get_room_for_control(request)

    async with room.lock:
        room.queue.clear()
        if room.current is None:
            room.schedule_delete()

    return web.json_response({"queue": []})
