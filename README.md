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
- The built-in browser player currently reads room state and uses WebRTC signaling endpoints without a bearer token. Treat room IDs as shareable access links, and do not expose this server to untrusted users if rooms must be confidential. Full per-room invitation authorization is not yet implemented.
- Only provide track paths from trusted sources. The queue API accepts a server-side file path; never let untrusted users submit arbitrary paths.

## Documentation

- [cURL API reference](docs/curl_methods_for_interaction/README.md) — HTTP endpoint reference.
- [Player functions](docs/player_functions/README.md) — optional Python `Room`, `Queue`, and `Playback` APIs.
- [Custom endpoints](docs/custom_endpoints/README.md) — register custom pages and API handlers.

## License

GNU General Public License v3. See [LICENSE](LICENSE).
