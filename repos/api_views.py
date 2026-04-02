from django.http import JsonResponse, Http404
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_http_methods
from config.decorators import require_api_key, verify_api_key
from .models import Repo

def serialize_repo(repo):
    return {
        'id': repo.id,
        'name': repo.name,
        'url': repo.url,
        'is_private': repo.is_private,
        'last_check_date': repo.last_check_date.isoformat() if repo.last_check_date else None,
        'last_import_date': repo.last_import_date.isoformat() if repo.last_import_date else None,
    }

@require_api_key('READ')
@require_http_methods(["GET"])
def get_repos(request):
    """Return a list of repos."""
    repos = Repo.objects.all()
    data = [serialize_repo(repo) for repo in repos]
    return JsonResponse({'data': data})

@require_http_methods(["GET", "DELETE"])
def get_repo(request, pk):
    """GET: Return details of a specific repo. DELETE: Remove it (WRITE key)."""
    perm = 'WRITE' if request.method == 'DELETE' else 'READ'
    error = verify_api_key(request, perm)
    if error:
        return error

    repo = get_object_or_404(Repo, pk=pk)

    if request.method == 'DELETE':
        repo.delete()
        return JsonResponse({'status': 'deleted'}, status=200)

    return JsonResponse({'data': serialize_repo(repo)})
