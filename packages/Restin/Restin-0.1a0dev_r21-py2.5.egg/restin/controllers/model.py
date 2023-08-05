from restin.lib.base import *
from paste.deploy.converters import asbool


class ModelController(RestController):
    def index(self):
        self.application.model_entities
        return self._render_response()

    def _init_entity(self):
        pass
