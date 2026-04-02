from django.http import JsonResponse, Http404
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_http_methods
from config.decorators import require_api_key, verify_api_key
from .models import Connector

def serialize_connector(connector):
    return {
        'id': connector.id,
        'name': connector.name,
        'description': connector.description,
        'installed': connector.installed,
        'enabled': connector.enabled,
        'domain': connector.domain,
    }

@require_api_key('READ')
@require_http_methods(["GET"])
def get_connectors(request):
    """Return a list of connectors."""
    connectors = Connector.objects.all()
    data = [serialize_connector(connector) for connector in connectors]
    return JsonResponse({'data': data})

@require_http_methods(["GET", "DELETE"])
def get_connector(request, pk):
    """GET: Return details of a specific connector. DELETE: Remove it (WRITE key)."""
    perm = 'WRITE' if request.method == 'DELETE' else 'READ'
    error = verify_api_key(request, perm)
    if error:
        return error

    connector = get_object_or_404(Connector, pk=pk)

    if request.method == 'DELETE':
        connector.delete()
        return JsonResponse({'status': 'deleted'}, status=200)

    return JsonResponse({'data': serialize_connector(connector)})
