from aiohttp import web
from aiortc.sdp import candidate_from_sdp

from pyLiveMusic._logger import logs


async def offer(request):
    try:
        room_id = request.match_info["room_id"]

        room = request.app["state"].rooms.get(room_id)

        if room is None:
            raise web.HTTPNotFound(text="Room not found")

        request.app["auth"]._verify_room_access(request, room)
        data = await request.json()

        sdp = data.get("sdp")

        if not sdp:
            raise web.HTTPBadRequest(text="Missing SDP")

        peer = await room.add_peer()

        try:
            answer = await room.offer(peer, sdp)

        except Exception:
            await room.remove_peer(peer)
            raise

        return web.json_response({
            "peer_id": peer.id,
            "type": answer.type,
            "sdp": answer.sdp,
        })

    except web.HTTPException:
        raise

    except Exception:
        logs.exception("[WEBRTC] Offer error")
        raise


async def candidate(request):
    try:
        room_id = request.match_info["room_id"]

        room = request.app["state"].rooms.get(room_id)

        if room is None:
            raise web.HTTPNotFound(
                text="Room not found"
            )

        request.app["auth"]._verify_room_access(request, room)
        data = await request.json()

        peer_id = data.get("peer_id")

        if not peer_id:
            raise web.HTTPBadRequest(
                text="Missing peer_id"
            )

        peer = room.get_peer(peer_id)

        if peer is None:
            raise web.HTTPNotFound(
                text="Peer not found"
            )

        value = data.get("candidate")

        if not value:
            return web.json_response({
                "ok": True
            })

        candidate_sdp = value.get("candidate")

        if not candidate_sdp:
            return web.json_response({
                "ok": True
            })

        try:
            ice = candidate_from_sdp(candidate_sdp)

        except Exception as error:
            raise web.HTTPBadRequest(
                text=f"Invalid ICE candidate: {error}"
            )

        ice.sdpMid = value.get("sdpMid")
        ice.sdpMLineIndex = value.get("sdpMLineIndex")

        await peer.add_candidate(ice)

        return web.json_response({
            "ok": True
        })

    except web.HTTPException:
        raise

    except Exception:
        logs.exception("[WEBRTC] Candidate error")
        raise