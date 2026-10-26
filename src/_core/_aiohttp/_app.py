from aiohttp import web

from pyLiveMusic._logger import logs

from _api._routes import (
    queue,
    rooms,
    webrtc,
    frontend,
    playback,
)
from _api.rooms import (
    create_room,
    end_room,
    get_room,
)

from _api.playback import (
    pause,
    resume,
    skip,
    volume,
    shuffle,
    repeat,
    ascending,
    descending,
    seek_front,
    seek_back,
    quality,
)

from _api.queue import (
    get_queue,
    add_track,
    remove_track,
    clear_queue,
)

from _utils._settings import STATIC_DIR
from _core._core_engine._webrtc.signaling import (
    offer,
    candidate,
)
from _core._core_func._state._data_state import _data_state
from _core._aiohttp._endpoints import register_endpoint


async def on_startup(app):
    state = app["state"]
    logs.info("Starting server...")
    await state.storage.connect()
    await state.rooms.start()


async def on_shutdown(app):
    state = app["state"]
    logs.info("Shutting down...")
    await state.rooms.shutdown()
    await state.storage.close()
    logs.info("Server stopped")


def create_app(auth, state, endpoints=None):
    app = web.Application()
    app["auth"] = auth
    app["state"] = state

    # Never log the bearer token: logs are commonly forwarded to third parties.
    logs.info("API authentication is enabled.")

    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)

    endpoints = endpoints or {}

    if frontend.room not in endpoints:
        app.router.add_get(
            frontend.room,
            lambda request: web.FileResponse(STATIC_DIR / "audio.html"),
        )

    app.router.add_static(frontend.static, STATIC_DIR)

    for endpoint in endpoints.values():
        register_endpoint(app, endpoint)

    app.router.add_get(rooms.get_room, get_room)
    app.router.add_post(rooms.end_room, end_room)
    app.router.add_post(rooms.create_room, create_room)

    app.router.add_post(playback.pause, pause)
    app.router.add_post(playback.resume, resume)
    app.router.add_post(playback.skip, skip)
    app.router.add_post(playback.volume, volume)
    app.router.add_post(playback.shuffle, shuffle)
    app.router.add_post(playback.repeat, repeat)
    app.router.add_post(playback.ascending, ascending)
    app.router.add_post(playback.descending, descending)
    app.router.add_post(playback.seek_front, seek_front)
    app.router.add_post(playback.seek_back, seek_back)
    app.router.add_post(playback.quality, quality)

    app.router.add_get(queue.get_queue, get_queue)
    app.router.add_post(queue.add_track, add_track)
    app.router.add_post(queue.remove_track, remove_track)
    app.router.add_post(queue.clear_queue, clear_queue)

    app.router.add_post(webrtc.offer, offer)
    app.router.add_post(
        "/api/rooms/{room_id}/webrtc/candidate",
        candidate,
    )

    return app


async def _start(host, port, auth, storage, endpoints=None):
    app = create_app(
        auth=auth,
        state=_data_state(storage),
        endpoints=endpoints,
    )

    runner = web.AppRunner(app)
    await runner.setup()

    site = web.TCPSite(runner, host, port)
    await site.start()

    logs.info(f"Server started on http://{host}:{port}")
    return runner
