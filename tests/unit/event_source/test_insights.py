import asyncio
import pytest
import aiohttp

from extensions.eda.plugins.event_source.insights import main as insights_main


async def start_server(queue, args):
    await insights_main(queue, args)


async def post_code(server_task, args, payload, headers=None):
    url = f'http://{args["host"]}:{args["port"]}/endpoint'

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, headers=headers):
            pass

    server_task.cancel()


async def cancel_code(server_task):
    server_task.cancel()


@pytest.mark.asyncio
async def test_cancel():
    queue = asyncio.Queue()

    args = {"host": "127.0.0.1", "port": 8001}
    plugin_task = asyncio.create_task(start_server(queue, args))
    cancel_task = asyncio.create_task(cancel_code(plugin_task))

    with pytest.raises(asyncio.CancelledError):
        await asyncio.gather(plugin_task, cancel_task)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "token,auth_header",
    [
        pytest.param(None, None, id="no_token"),
        pytest.param("secret", "Authorization", id="bearer_token"),
        pytest.param("secret", "X-Insight-Token", id="x_insights_token"),
    ],
)
async def test_post_endpoint(token, auth_header, request):
    queue = asyncio.Queue()

    args = {"host": "127.0.0.1", "port": 8000 + (hash(request.node.callspec.id) % 1000)}
    if token:
        args["token"] = token

    plugin_task = asyncio.create_task(start_server(queue, args))

    headers = {}
    if auth_header:
        headers[auth_header] = f"Bearer {token}" if auth_header == "Authorization" else token

    payload = {
        "eventdata": "insights"
    }

    post_task = asyncio.create_task(post_code(plugin_task, args, payload, headers=headers))

    await asyncio.gather(plugin_task, post_task)

    data = await asyncio.wait_for(queue.get(), 1)
    assert "payload" in data
    assert "meta" in data
    assert "eventdata" in data["payload"]
    assert data["payload"]["eventdata"] == "insights"
    assert "endpoint" in data["meta"]
    assert data["meta"]["endpoint"] == "endpoint"
