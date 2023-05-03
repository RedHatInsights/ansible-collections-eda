import asyncio
import pytest
import aiohttp

from extensions.eda.plugins.event_source.insights import main as insights_main


async def start_server(queue, args):
    await insights_main(queue, args)


async def post_code(server_task, args, payload):
    url = f'http://{args["host"]}:{args["port"]}/endpoint'

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload):
            pass

    server_task.cancel()


async def cancel_code(server_task):
    server_task.cancel()


@pytest.mark.asyncio
async def test_cancel():
    queue = asyncio.Queue()

    args = {"host": "127.0.0.1", "port": 8000}
    plugin_task = asyncio.create_task(start_server(queue, args))
    cancel_task = asyncio.create_task(cancel_code(plugin_task))

    with pytest.raises(asyncio.CancelledError):
        await asyncio.gather(plugin_task, cancel_task)


@pytest.mark.asyncio
async def test_post_endpoint():
    queue = asyncio.Queue()

    args = {"host": "127.0.0.1", "port": 8000}
    plugin_task = asyncio.create_task(start_server(queue, args))

    payload = {
        "eventdata": "insights"
    }

    post_task = asyncio.create_task(post_code(plugin_task, args, payload))

    await asyncio.gather(plugin_task, post_task)

    data = await queue.get()
    assert "payload" in data
    assert "meta" in data
    assert "eventdata" in data["payload"]
    assert data["payload"]["eventdata"] == "insights"
    assert "endpoint" in data["meta"]
    assert data["meta"]["endpoint"] == "endpoint"
