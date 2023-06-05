"""
insights.py

An ansible-rulebook event source module for receiving Red Hat Insights events.

Arguments:
    host:     The hostname to listen to. Set to 0.0.0.0 to listen on all
              interfaces. Defaults to 127.0.0.1
    port:     The TCP port to listen to.  Defaults to 5000
    token:    The optional authentication token expected from client
    certfile: The optional path to a certificate file to enable TLS support
    keyfile:  The optional path to a key file to be used together with certfile
    password: The optional password to be used when loading the certificate chain

"""

import asyncio
import logging
import ssl
from typing import Any, Callable, Dict

from aiohttp import web

INSIGHTS_TOKEN_HEADER = "X-Insight-Token"
AUTHORIZATION_HEADER = "Authorization"

logger = logging.getLogger(__name__)
routes = web.RouteTableDef()


def format_event(payload: Dict[str, Any], endpoint: str, headers: Dict[str, str]):
    return {
        "payload": payload,
        "meta": {"endpoint": endpoint, "headers": headers},
    }


@routes.post(r"/{endpoint:.*}")
async def webhook(request: web.Request):
    try:
        payload = await request.json()
    except ValueError:
        raise web.HTTPBadRequest(reason="Malformed JSON request")

    endpoint = request.match_info["endpoint"]
    headers = dict(request.headers)
    headers.pop(AUTHORIZATION_HEADER, None)
    headers.pop(INSIGHTS_TOKEN_HEADER, None)

    event = format_event(payload, endpoint, headers)
    await request.app["queue"].put(event)
    return web.Response(text=endpoint)


def get_request_token(request: web.Request):
    if INSIGHTS_TOKEN_HEADER in request.headers:
        return request.headers[INSIGHTS_TOKEN_HEADER]
    elif AUTHORIZATION_HEADER in request.headers:
        scheme, _, token = request.headers[AUTHORIZATION_HEADER].strip().partition(" ")
        if scheme == "Bearer":
            return token


@web.middleware
async def authenticate(request: web.Request, handler: Callable):
    request_token = get_request_token(request)
    if request_token is None:
        raise web.HTTPUnauthorized(reason="Missing authorization token")
    if request_token != request.app["token"]:
        raise web.HTTPUnauthorized(reason="Invalid authorization token")

    return await handler(request)


async def main(queue: asyncio.Queue, args: Dict[str, Any]):
    middlewares = []
    if args.get("token"):
        middlewares = [authenticate]

    app = web.Application(middlewares=middlewares)
    app["token"] = args.get("token")
    app["queue"] = queue
    app.add_routes(routes)

    context = None
    if "certfile" in args:
        certfile = args.get("certfile")
        keyfile = args.get("keyfile", None)
        password = args.get("password", None)
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        try:
            context.load_cert_chain(certfile, keyfile, password)
        except Exception:
            logger.error("Failed to load certificates. Check they are valid")
            raise

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(
        runner,
        args.get("host") or "localhost",
        args.get("port") or 5000,
        ssl_context=context,
    )
    await site.start()

    try:
        await asyncio.Future()
    except asyncio.CancelledError:
        logger.info("Insights Plugin Task Cancelled")
    finally:
        await runner.cleanup()


if __name__ == "__main__":
    class MockQueue:
        async def put(self, event):
            print(event)

    asyncio.run(
        main(MockQueue(), {"port": 2345})
    )
