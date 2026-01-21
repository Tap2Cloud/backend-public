from t2c_backend.core.repository import BaseRepository
from t2c_backend.models import Taxonomy


class TaxonomyService:
    _model = Taxonomy

    def __init__(self, app, session) -> None:
        self.app = app
        self.repository = BaseRepository(app, session, self._model)

    async def get_taxonomies(self):
        return await self.repository.list()


def setup(app, session, *args, **kwargs):
    return app.add_service(TaxonomyService(app, session), session.info["session_id"])
