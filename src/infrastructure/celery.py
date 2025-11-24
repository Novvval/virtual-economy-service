import asyncio
import threading

from celery import Celery

from . import tasks
from .config import Settings
from .container import Container


def create_celery_app():
    settings = Settings()
    container = Container()
    container.config.from_pydantic(settings)
    container.wire([tasks])

    app = Celery("virtual-economy-app")

    redis_url = f"redis://{settings.redis_host}:{settings.redis_port}"

    app.conf.update(
        broker_url=redis_url,
        result_backend=redis_url,
        beat_schedule=settings.celery_beat_schedule,
        task_serializer="json",
        accept_content=["json"],
        result_serializer="json",
        timezone="UTC",
        enable_utc=True,
    )
    app.autodiscover_tasks()
    app.container = container

    app.loop = asyncio.get_event_loop()
    app.loop_runner = threading.Thread(
        target=app.loop.run_forever,
        daemon=True,
    )
    app.loop_runner.start()
    return app


app = create_celery_app()
