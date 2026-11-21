from redis.asyncio import Redis as AsyncRedis


class Redis:
    def __init__(self, app) -> None:
        self.app = app
        self.client = AsyncRedis.from_url(app.config.REDIS_URL, decode_responses=True)


async def setup(app):
    return app.add_client(Redis(app))
