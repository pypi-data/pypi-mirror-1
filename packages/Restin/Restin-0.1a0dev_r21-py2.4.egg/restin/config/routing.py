"""
Setup your Routes options here
"""
import os
from routes import Mapper


GET_condition = dict(method=['GET'])
POST_condition = dict(method=['POST'])
PUT_condition = dict(method=['PUT'])
DELETE_condition = dict(method=['DELETE'])

def make_map(global_conf={}, app_conf={}):
    root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    map = Mapper(directory=os.path.join(root_path, 'controllers'))
    map.connect('error/:action/:id', controller='error')

    map.resource('application', 'applications')

    _app_resource = dict(_member_name='application',
                         _collection_name='applications')
    app_resource = dict(member_name='application',
                        collection_name='applications')

    map.connect('applications/:application_id/model', 
                controller='model', action='index',
                _member_name='model', _collection_name='model',
                _parent_resource=app_resource)

    base_route = 'applications/:application_id/:controller/:entity_name'
    resource(map, base_route)

    map.connect('', controller='applications', action='index', **_app_resource)

    map.connect('*url', controller='template', action='view')
    return map

def resource(map, base_route):
    """Manually create the equivalent of the routes ``map.resource`` generates.

    ``map``
        The Routes ``Mapper`` object

    ``base_route``
        The route (string) up to but not including the :id, :action, and
        :format

        For example::

            "applications/:application_id/:controller/:entity_name"

    """
    kw = dict(action='create', conditions=POST_condition)
    map.connect(base_route, **kw)

    kw = dict(action='index', conditions=GET_condition)
    map.connect(base_route, **kw)
    map.connect(base_route + '.:(format)', **kw)

    kw = dict(action='new', conditions=GET_condition)
    map.connect(base_route + '/new', **kw)
    map.connect(base_route + '/new.:(format)', **kw)

    kw = dict(action='update', conditions=PUT_condition)
    map.connect(base_route + '/:id', **kw)

    kw = dict(action='delete', conditions=DELETE_condition)
    map.connect(base_route + '/:id', **kw)

    kw = dict(action='edit', conditions=GET_condition)
    map.connect(base_route + '/:(id);edit', **kw)
    map.connect(base_route + '/:(id).:(format);edit', **kw)

    kw = dict(action='show', conditions=GET_condition)
    map.connect(base_route + '/:id', **kw)
    map.connect(base_route + '/:(id).:(format)', **kw)
