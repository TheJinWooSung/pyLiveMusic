from aiohttp import web


from _api._errors import json_error


def get_room(request):

    room = request.app["state"].rooms.get(request.match_info["room_id"])
    if room is None:
        raise web.HTTPNotFound(text="ROOM_NOT_FOUND")

    request.app["auth"]._verify_room_control(request, room)
    return room


async def pause(request):

    room = get_room(request)

    try:
        await room.pause()
    except ValueError as error:
        return json_error(str(error))

    return web.json_response(room.state())


async def resume(request):

    room = get_room(request)

    try:
        await room.resume()
    except ValueError as error:
        return json_error(str(error))

    return web.json_response(room.state())


async def skip(request):
    
    room = get_room(request)

    try:
        await room.skip()
    except ValueError as error:
        return json_error(str(error))

    return web.json_response(room.state_or_not_playing())


async def volume(request):

    room = get_room(request)
    data = await request.json()

    try:
        await room.set_volume(data["volume"])

    except (
        KeyError,
        ValueError,
    ) as error:

        code = (
            str(error)
            if isinstance(error, ValueError)
            else "INVALID_VOLUME"
        )

        return json_error(code)

    return web.json_response(room.state_or_not_playing())


async def shuffle(request):

    room = get_room(request)
    data = await request.json()

    await room.set_shuffle(data.get("enabled", False))

    return web.json_response(room.state_or_not_playing())


async def repeat(request):

    room = get_room(request)
    data = await request.json()

    try:
        await room.set_repeat(data["mode"])

    except (
        KeyError,
        ValueError,
    ) as error:

        code = (
            str(error)
            if isinstance(error, ValueError)
            else "INVALID_REPEAT_MODE"
        )

        return json_error(code)

    return web.json_response(room.state_or_not_playing())


async def ascending(request):

    room = get_room(request)

    try:
        await room.set_order("ascending")
    except ValueError as error:
        return json_error(str(error))

    return web.json_response(room.state_or_not_playing())


async def descending(request):

    room = get_room(request)

    try:
        await room.set_order("descending")
    except ValueError as error:
        return json_error(str(error))

    return web.json_response(room.state_or_not_playing())


async def seek_front(request):

    room = get_room(request)
    data = await request.json()

    try:
        await room.seek_front(data["seconds"])

    except (
        KeyError,
        ValueError,
    ) as error:

        code = (
            str(error)
            if isinstance(error, ValueError)
            else "INVALID_SEEK_SECONDS"
        )

        return json_error(code)

    return web.json_response(room.state())


async def seek_back(request):

    room = get_room(request)
    data = await request.json()

    try:
        await room.seek_back(data["seconds"])
    except (
        KeyError,
        ValueError,
    ) as error:

        code = (
            str(error)
            if isinstance(error, ValueError)
            else "INVALID_SEEK_SECONDS"
        )

        return json_error(code)

    return web.json_response(room.state())


async def quality(request):

    room = get_room(request)
    data = await request.json()

    try:
        await room.set_quality(data["quality"])

    except (
        KeyError,
        ValueError,
    ) as error:

        code = (
            str(error)
            if isinstance(error, ValueError)
            else "INVALID_AUDIO_QUALITY"
        )

        return json_error(code)

    return web.json_response(room.state_or_not_playing())