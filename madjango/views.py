import json
from django.http import HttpResponse, Http404
from utils import api_call
from django.contrib.admin.views.decorators import staff_member_required


@staff_member_required
def api(request):
    search = request.GET.get('search', False)
    if not search:
        raise Http404
    search = '{}%'.format(search)
    data = api_call('catalog_product.list', {'name': {'like': search}})
    return HttpResponse(json.dumps(data), mimetype='application/json')

