from restin.lib.base import *


class DataController(restler.BaseController(restin_model)):
    def __init__(self):
        route = request.environ['routes.route']
        route_info = request.environ['pylons.routes_dict']

        application_id = route_info['application_id']
        app = self._get_entity_or_404(restin_model.Application,
                                      application_id)
        self._model = app.model

        entity_name = route_info['entity_name']
        collection_name = '%ss' % entity_name

        route.member_name = entity_name
        route.collection_name = collection_name

        route.parent_resource = dict(member_name='application',
                                     collection_name='applications')

        super(DataController, self).__init__()
