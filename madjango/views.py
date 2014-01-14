import json
from django.http import HttpResponse, Http404
from utils import api_call

def api(request):
    search = request.GET.get('search', False)
    if not search:
        raise Http404
    search = '{}%'.format(search)
    data = api_call('catalog_product.list', {'name': {'like': search}})
    return HttpResponse(json.dumps(data), mimetype='application/json')

