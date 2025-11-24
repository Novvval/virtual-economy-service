import asyncio
import logging

from aiostream import stream
from celery import shared_task, states, Task
from celery.exceptions import Ignore
from dependency_injector.wiring import inject, Provide

from .container import Container
from ..interfaces.cache import Cache


_logger = logging.getLogger(__name__)


@shared_task(bind=True)
def clear_inventory_cache_task(self):
    from .celery import app

    coro = clear_inventory_cache(self)
    asyncio.run_coroutine_threadsafe(
        coro=coro,
        loop=app.loop,
    )


@inject
async def clear_inventory_cache(task: Task, cache: Cache = Provide[Container.cache]):
    try:
        pattern = "inventory:*"
        items = 0
        async for chunk in stream.chunks(cache.iter(pattern), 1000):
            coros = [cache.delete(key) for key in chunk]
            await asyncio.gather(*coros)
            items += len(chunk)
        msg = f"Deleted {items} cached user inventories"
        _logger.info(msg)
        task.update_state(state=states.SUCCESS, meta=msg)
    except Exception as e:
        task.update_state(state=states.FAILURE, meta="Failed to delete inventory cache")
        _logger.warning(str(e))
        raise Ignore()
