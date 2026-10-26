# pyLiveMusic API — cURL Reference

This document provides examples for interacting with the `pyLiveMusic` HTTP API using `curl`.

## Server

By default, the server runs at:

```text
http://localhost:8000
```

### Authentication

Authenticated endpoints require a Bearer token:

```text
Authorization: Bearer <key>
```

Replace `<key>` with the same `AUTH_KEY` configured for the server and caller. The key is never printed to logs; if omitted, the client generates a random key at startup.

---

# 1. Rooms

## Create a room

Creates a live room and persists its metadata. The response includes `control_token` for room controls, plus `player_token` and `player_path` for listening. Share `https://your-host.example` + `player_path` with listeners; keep `control_token` private.

```bash
curl -X POST http://localhost:8000/api/rooms \
  -H "Authorization: Bearer 124" \
  -H "Content-Type: application/json" \
  -d '{"name":"My Room"}'
```

Example response:

```json
{
  "room_id": "bdf36a19a0a9",
  "name": "My Room",
  "participants": 0,
  "playing": false,
  "position": 0.0,
  "duration": 0.0,
  "volume": 1.0,
  "quality": "high",
  "shuffle": false,
  "repeat": "none",
  "order": "ascending",
  "current": null,
  "queue": []
}
```

Save the returned room ID:

```bash
ROOM_ID="bdf36a19a0a9"
```

## Get a room

Returns the current live runtime state of a room.

```bash
curl http://localhost:8000/api/rooms/$ROOM_ID
```


## End a room

Ends the live room and removes its persisted room record.

```bash
curl -X POST http://localhost:8000/api/rooms/$ROOM_ID/end \
  -H "Authorization: Bearer 124"
```

Example response:

```json
{
  "status": "ended"
}
```

---

# 2. Queue

## Get the queue

Returns the current track and queued tracks for a room.

```bash
curl http://localhost:8000/api/rooms/$ROOM_ID/queue
```

Example response:

```json
{
  "room_id": "bdf36a19a0a9",
  "current": {
    "id": "8d2d...",
    "title": "My Song"
  },
  "queue": []
}
```

## Add a track

Adds an audio file to the room queue.

```bash
curl -X POST http://localhost:8000/api/rooms/$ROOM_ID/queue/add \
  -H "Authorization: Bearer 124" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "My Song",
    "path": "/path/to/audio/audio.mp3"
  }'
```

Example response:

```json
{
  "id": "8d2d...",
  "title": "My Song"
}
```

Save the returned track ID:

```bash
TRACK_ID="8d2d..."
```

> If there is no currently playing track, the first track added may start playing immediately instead of remaining only in the queue.

## Remove a queued track

```bash
curl -X POST http://localhost:8000/api/rooms/$ROOM_ID/queue/$TRACK_ID/remove \
  -H "Authorization: Bearer 124"
```

Example:

```bash
curl -X POST http://localhost:8000/api/rooms/bdf36a19a0a9/queue/8d2d1234/remove \
  -H "Authorization: Bearer 124"
```

> This endpoint removes a queued item. It is not intended to remove the currently playing track.

## Clear the queue

```bash
curl -X POST http://localhost:8000/api/rooms/$ROOM_ID/queue/clear \
  -H "Authorization: Bearer 124"
```

---

# 3. Playback

## Pause

Pauses the current track.

```bash
curl -X POST http://localhost:8000/api/rooms/$ROOM_ID/pause \
  -H "Authorization: Bearer 124"
```

## Resume

Resumes playback.

```bash
curl -X POST http://localhost:8000/api/rooms/$ROOM_ID/resume \
  -H "Authorization: Bearer 124"
```

## Skip

Skips the currently playing track and moves to the next available track.

```bash
curl -X POST http://localhost:8000/api/rooms/$ROOM_ID/skip \
  -H "Authorization: Bearer 124"
```

---

# 4. Volume

Volume is represented as a value between `0` and `1`.

* `0` — muted
* `0.5` — 50%
* `1.0` — 100%

## 50% volume

```bash
curl -X POST http://localhost:8000/api/rooms/$ROOM_ID/volume \
  -H "Authorization: Bearer 124" \
  -H "Content-Type: application/json" \
  -d '{"volume":0.5}'
```

## 100% volume

```bash
curl -X POST http://localhost:8000/api/rooms/$ROOM_ID/volume \
  -H "Authorization: Bearer 124" \
  -H "Content-Type: application/json" \
  -d '{"volume":1.0}'
```

## Mute

```bash
curl -X POST http://localhost:8000/api/rooms/$ROOM_ID/volume \
  -H "Authorization: Bearer 124" \
  -H "Content-Type: application/json" \
  -d '{"volume":0}'
```

---

# 5. Shuffle

## Enable shuffle

```bash
curl -X POST http://localhost:8000/api/rooms/$ROOM_ID/shuffle \
  -H "Authorization: Bearer 124" \
  -H "Content-Type: application/json" \
  -d '{"enabled":true}'
```

## Disable shuffle

```bash
curl -X POST http://localhost:8000/api/rooms/$ROOM_ID/shuffle \
  -H "Authorization: Bearer 124" \
  -H "Content-Type: application/json" \
  -d '{"enabled":false}'
```

---

# 6. Repeat

Supported repeat modes:

```text
none
once
all
```

## No repeat

```bash
curl -X POST http://localhost:8000/api/rooms/$ROOM_ID/repeat \
  -H "Authorization: Bearer 124" \
  -H "Content-Type: application/json" \
  -d '{"mode":"none"}'
```

## Repeat once

```bash
curl -X POST http://localhost:8000/api/rooms/$ROOM_ID/repeat \
  -H "Authorization: Bearer 124" \
  -H "Content-Type: application/json" \
  -d '{"mode":"once"}'
```

## Repeat all

```bash
curl -X POST http://localhost:8000/api/rooms/$ROOM_ID/repeat \
  -H "Authorization: Bearer 124" \
  -H "Content-Type: application/json" \
  -d '{"mode":"all"}'
```

---

# 7. Playback Order

## Ascending

```bash
curl -X POST http://localhost:8000/api/rooms/$ROOM_ID/order/ascending \
  -H "Authorization: Bearer 124"
```

## Descending

```bash
curl -X POST http://localhost:8000/api/rooms/$ROOM_ID/order/descending \
  -H "Authorization: Bearer 124"
```

---

# 8. Seek

## Seek forward

Moves the playback position forward by the specified number of seconds.

```bash
curl -X POST http://localhost:8000/api/rooms/$ROOM_ID/seek/front \
  -H "Authorization: Bearer 124" \
  -H "Content-Type: application/json" \
  -d '{"seconds":10}'
```

## Seek backward

Moves the playback position backward by the specified number of seconds.

```bash
curl -X POST http://localhost:8000/api/rooms/$ROOM_ID/seek/back \
  -H "Authorization: Bearer 124" \
  -H "Content-Type: application/json" \
  -d '{"seconds":5}'
```

---

# 9. Audio Quality

Supported quality levels:

```text
low
medium
high
highest
peak
```

## Low — 48 kbps

```bash
curl -X POST http://localhost:8000/api/rooms/$ROOM_ID/quality \
  -H "Authorization: Bearer 124" \
  -H "Content-Type: application/json" \
  -d '{"quality":"low"}'
```

## Medium — 96 kbps

```bash
curl -X POST http://localhost:8000/api/rooms/$ROOM_ID/quality \
  -H "Authorization: Bearer 124" \
  -H "Content-Type: application/json" \
  -d '{"quality":"medium"}'
```

## High — 128 kbps

```bash
curl -X POST http://localhost:8000/api/rooms/$ROOM_ID/quality \
  -H "Authorization: Bearer 124" \
  -H "Content-Type: application/json" \
  -d '{"quality":"high"}'
```

## Highest — 256 kbps

```bash
curl -X POST http://localhost:8000/api/rooms/$ROOM_ID/quality \
  -H "Authorization: Bearer 124" \
  -H "Content-Type: application/json" \
  -d '{"quality":"highest"}'
```

## Peak — 320 kbps

```bash
curl -X POST http://localhost:8000/api/rooms/$ROOM_ID/quality \
  -H "Authorization: Bearer 124" \
  -H "Content-Type: application/json" \
  -d '{"quality":"peak"}'
```

---

# 10. WebRTC

The WebRTC signaling endpoint is used by the browser or client to establish a WebRTC audio connection.

## WebRTC offer

```text
POST /api/rooms/{room_id}/webrtc/offer
```

The request body contains the SDP offer generated by the WebRTC peer:

```json
{
  "type": "offer",
  "sdp": "v=0\r\n..."
}
```

Open the room in a browser:

```text
http://localhost:8000/room/$ROOM_ID
```

> WebRTC signaling is normally handled by the browser or client rather than manually with `curl`.

---

# 11. Static Web Interface

## Main page

```text
http://localhost:8000/
```

## Room page

```text
http://localhost:8000/room/$ROOM_ID
```

---

# 12. Endpoint Reference

| Method | Endpoint                                       | Authentication |
| ------ | ---------------------------------------------- | -------------- |
| `POST` | `/api/rooms`                                   | Yes            |
| `GET`  | `/api/rooms/{room_id}`                         | No             |
| `POST` | `/api/rooms/{room_id}/end`                     | Yes            |
| `GET`  | `/api/rooms/{room_id}/queue`                   | No             |
| `POST` | `/api/rooms/{room_id}/queue/add`               | Yes            |
| `POST` | `/api/rooms/{room_id}/queue/{track_id}/remove` | Yes            |
| `POST` | `/api/rooms/{room_id}/queue/clear`             | Yes            |
| `POST` | `/api/rooms/{room_id}/pause`                   | Yes            |
| `POST` | `/api/rooms/{room_id}/resume`                  | Yes            |
| `POST` | `/api/rooms/{room_id}/skip`                    | Yes            |
| `POST` | `/api/rooms/{room_id}/volume`                  | Yes            |
| `POST` | `/api/rooms/{room_id}/shuffle`                 | Yes            |
| `POST` | `/api/rooms/{room_id}/repeat`                  | Yes            |
| `POST` | `/api/rooms/{room_id}/order/ascending`         | Yes            |
| `POST` | `/api/rooms/{room_id}/order/descending`        | Yes            |
| `POST` | `/api/rooms/{room_id}/seek/front`              | Yes            |
| `POST` | `/api/rooms/{room_id}/seek/back`               | Yes            |
| `POST` | `/api/rooms/{room_id}/quality`                 | Yes            |
| `POST` | `/api/rooms/{room_id}/webrtc/offer`            | No*            |
| `POST` | `/api/rooms/{room_id}/webrtc/candidate`        | No*            |

* WebRTC signaling is normally handled by the browser or client rather than manually through `curl`.
