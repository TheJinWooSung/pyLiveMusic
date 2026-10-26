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

- Control endpoints accept the server-wide `Authorization: Bearer <AUTH_KEY>` credential or the room-specific `control_token` returned when creating a room.
- Do not publish the key, commit it to source control, or print it in logs.
- If another service needs to call the API, configure the same strong `AUTH_KEY` in the server and caller.
- Serve the application behind HTTPS in production.
- Room creation returns separate credentials: `control_token` for playback/queue/room controls, and `player_token` plus `player_path` for listeners. Share `https://your-host.example` + `player_path` with listeners; its `#token` fragment is read by the browser and sent only in authorization headers.
- The browser player requires a valid room credential for room-state reads and WebRTC signaling. Control endpoints accept either the server-wide `AUTH_KEY` or that room’s `control_token`.
- Keep control credentials private and share player invite links only with intended listeners. Use HTTPS in production; anyone with a player invite can listen to that room.
- Only provide track paths from trusted sources. The queue API accepts a server-side file path; never let untrusted users submit arbitrary paths.

## Tests

Run the focused authentication and queue authorization tests from the repository root:

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
```

## Documentation

- [cURL API reference](docs/curl_methods_for_interaction/README.md) — HTTP endpoint reference.
- [Player functions](docs/player_functions/README.md) — optional Python `Room`, `Queue`, and `Playback` APIs.
- [Custom endpoints](docs/custom_endpoints/README.md) — register custom pages and API handlers.

## License

GNU General Public License v3. See [LICENSE](LICENSE).
