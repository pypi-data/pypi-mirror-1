from pylons.database import create_engine

from sqlalchemy import MetaData

import elixir
from elixir import has_field, belongs_to, has_many, String
from elixir import Entity as ElixirEntity

import restler


metadata = MetaData()


class Application(elixir.Entity):
    has_field('title', String(31))
    has_field('package_name', String(31))
    has_field('egg_name', String(31))
    has_field('dburi', String(127))
    has_field('description', String)
    has_many('entities', of_kind='Entity')

    alternate_ids = ['package_name']

    @property
    def model(self):
        model = getattr(self, '_model', None)
        if model is None:
            imp_args = globals(), locals(), ['']
            base = __import__('%s.lib.base' % self.package_name, *imp_args)
            model = getattr(base, 'model', None)
            if model is None:
                model = __import__('%s.models' % package_name, *imp_args)
            engine = create_engine(uri=self.dburi, echo=0)
            restler.init_model(model)
            model.metadata.connect(engine)
            self._model = model
        return model

    @property
    def model_entities(self):
        entities = getattr(self, '_model_entities', None)
        if entities is None:
            entities = []
            for name, attr in self.model.__dict__.items():
                if hasattr(attr, 'c'):
                    entities.append(attr)
            self._model_entities = entities
        return entities

    def __str__(self):
        return 'Application: %s' % self.title

    def __repr__(self):
        return str(self)


class Entity(elixir.Entity):
    has_field('table', String(31))
    belongs_to('application', of_kind='Application')
