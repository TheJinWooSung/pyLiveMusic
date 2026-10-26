# pyLiveMusic

A Python framework for creating private rooms for live audio streaming with WebRTC.

## Installation

```bash
pip install -U pyLiveMusic
```

### Optional storage backends

- MongoDB: `pip install -U "pyLiveMusic[mongo]"`
- Redis: `pip install -U "pyLiveMusic[redis]"`
- MongoDB + Redis: `pip install -U "pyLiveMusic[all]"`

## Basic setup

```python
import asyncio

from pyLiveMusic import Client


async def main():
    # For integrations that call the HTTP API directly, provide a strong
    # secret through your deployment's secret manager or environment config.
    client = Client()
    try:
        await client.start()
        await client.run_until_disconnect()
    finally:
        await client.stop()


if __name__ == "__main__":
    asyncio.run(main())
```

## Authentication and deployment notes

- Control endpoints require an `Authorization: Bearer <AUTH_KEY>` header.
- Do not publish the key, commit it to source control, or print it in logs.
- If another service needs to call the API, configure the same strong `AUTH_KEY` in the server and caller.
- Serve the application behind HTTPS in production.
- Room creation returns a one-time-to-share player credential (`player_token`) and a relative invite path (`player_path`). Share the path as `https://your-host.example` + `player_path`; its `#token` fragment is read by the browser and sent only in authorization headers.
- The browser player requires the room-specific credential for room-state reads and WebRTC signaling. The server-wide `AUTH_KEY` remains required for room creation, playback controls, and queue management.
- Keep player invite links private and use HTTPS in production. Anyone with a room invite link can listen to that room; the token is not a substitute for user identity or revocation.
- Only provide track paths from trusted sources. The queue API accepts a server-side file path; never let untrusted users submit arbitrary paths.

## Documentation

- [cURL API reference](docs/curl_methods_for_interaction/README.md) — HTTP endpoint reference.
- [Player functions](docs/player_functions/README.md) — optional Python `Room`, `Queue`, and `Playback` APIs.
- [Custom endpoints](docs/custom_endpoints/README.md) — register custom pages and API handlers.

## License

GNU General Public License v3. See [LICENSE](LICENSE).
