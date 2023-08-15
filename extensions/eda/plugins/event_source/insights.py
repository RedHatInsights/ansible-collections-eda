"""insights.py.

An ansible-rulebook event source module for receiving Red Hat Insights events.

Arguments:
---------
    host:     The hostname to listen to. Set to 0.0.0.0 to listen on all
              interfaces. Defaults to 0.0.0.0
    port:     The TCP port to listen to.  Defaults to 5000
    token:    The optional authentication token expected from client
    certfile: The optional path to a certificate file to enable TLS support
    keyfile:  The optional path to a key file to be used together with certfile
    password: The optional password to be used when loading the certificate chain

"""

# disable typing ruff checks to support older Python versions
# ruff: noqa: UP006 UP007 UP035

from __future__ import annotations

import asyncio
import logging
import ssl
from typing import TYPE_CHECKING, Any, Dict, Union

from aiohttp import web

if TYPE_CHECKING:
    from collections.abc import Callable


INSIGHTS_TOKEN_HEADER = "X-Insight-Token"  # noqa: S105
AUTHORIZATION_HEADER = "Authorization"

logger = logging.getLogger(__name__)
routes = web.RouteTableDef()


def _format_event(
        payload: Dict[str, Any],
        endpoint: str,
        headers: Dict[str, str],
) -> Dict:
    return {
        "payload": payload,
        "meta": {"endpoint": endpoint, "headers": headers},
    }


@routes.post(r"/{endpoint:.*}")
async def webhook(request: web.Request) -> web.Response:
    """Event POST handler.

    Parameters
    ----------
    request : web.Request
        POST request.

    Returns
    -------
    web.Response
        Responses with 200 on succesful event procecing and returns
        endoint name used to call this API.

    Raises
    ------
    HTTPBadRequest
        If the event is incorrectly formatted to JSON.
    """
    try:
        payload = await request.json()
    except ValueError as ex:
        raise web.HTTPBadRequest(reason="Malformed JSON request") from ex

    endpoint = request.match_info["endpoint"]
    headers = dict(request.headers)
    headers.pop(AUTHORIZATION_HEADER, None)
    headers.pop(INSIGHTS_TOKEN_HEADER, None)

    event = _format_event(payload, endpoint, headers)
    await request.app["queue"].put(event)
    return web.Response(text=endpoint)


def _get_request_token(request: web.Request) -> Union[None, str]:
    if INSIGHTS_TOKEN_HEADER in request.headers:
        return request.headers[INSIGHTS_TOKEN_HEADER]
    if AUTHORIZATION_HEADER in request.headers:
        scheme, _sep, token = \
            request.headers[AUTHORIZATION_HEADER].strip().partition(" ")
        if scheme == "Bearer":
            return token
        return None
    return None


@web.middleware
async def _authenticate(request: web.Request, handler: Callable) -> web.Response:
    request_token = _get_request_token(request)
    if request_token is None:
        raise web.HTTPUnauthorized(reason="Missing authorization token")
    if request_token != request.app["token"]:
        raise web.HTTPUnauthorized(reason="Invalid authorization token")

    return await handler(request)


async def main(queue: asyncio.Queue, args: Dict[str, Any]) -> None:
    """Entrypoint.

    Parameters
    ----------
    queue : asyncio.Queue
        Queue where the received events would be put for processing
        by Ansible Rulebook.
    args : Dict[str, Any]
        Configuration arguments set within rulebook for this EDA source.
        See full list at the top.

    Raises
    ------
    Exception
        If the configured certificate could not be loaded.
    """
    middlewares = []
    if args.get("token"):
        middlewares = [_authenticate]

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
            logger.exception("Failed to load certificates. Check they are valid")
            raise

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(
        runner,
        args.get("host") or "0.0.0.0",  # noqa: S104
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
    # pylint: disable=E0401, C0116, R0903, C0115
    class MockQueue:  # noqa: D101
        async def put(self, event):  # noqa: D102 ANN001 ANN101 ANN201
            print(event)  # noqa: T201

    asyncio.run(
        main(MockQueue(), {"port": 2345}),
    )
