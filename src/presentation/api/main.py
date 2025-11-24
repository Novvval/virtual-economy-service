from contextlib import asynccontextmanager

from slowapi.middleware import SlowAPIMiddleware
from starlette.responses import RedirectResponse

from src.infrastructure.config import Settings
from src.infrastructure.container import Container
from src.infrastructure.db import orm
from src.presentation.api.app import Application

from . import depends
from .depends import limiter
from .error_handlers import init_error_handlers
from .routes import products, users, analytics
from .schema.responses import COMMON_RESPONSES


@asynccontextmanager
async def lifespan(app: Application):
    orm.init_mappers()
    engine = app.container.engine()
    if app.container.config.debug():
        await orm.create_tables(engine)
    yield
    await app.container.shutdown_resources()


def init_routers(app: Application):
    app.include_router(products.router)
    app.include_router(users.router)
    app.include_router(analytics.router)


def create_app() -> Application:
    container = Container()
    container.config.from_pydantic(Settings())

    app = Application(
        title="Virtual Economy Service",
        version="0.1.0",
        lifespan=lifespan,
        debug=container.config.debug,
        responses=COMMON_RESPONSES,
        container=container
    )
    init_error_handlers(app)
    init_routers(app)
    app.add_middleware(SlowAPIMiddleware)
    app.state.limiter = limiter

    container.wire(modules=[products, users, analytics, depends])

    return app


app = create_app()


@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/")
async def index():
    return RedirectResponse("/docs")


if __name__ == "__main__":
    app = app
