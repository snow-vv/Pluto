# Create your views here.
from common.views import JsonView
from service.models import InitRelation


class ServiceRelationApiView(JsonView):
    permissions = ['service.relation']

    def get(self, request):
        init_list = InitRelation.objects.all()
        l = [
            {
                'src': items.src,
                'target': items.target,
                'weight': items.weight
            } for items in init_list
        ]
        nodes = set()
        for i in l:
            nodes.add(i['src'])
            nodes.add(i['target'])
        l.sort(key=lambda x: x['weight'])
        for index, rel in enumerate(l):
            rel['wide'] = int(index / 3 + 1)
        return {
            "nodes": list(nodes),
            "list": l
        }
