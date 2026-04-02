import json
from django.http import JsonResponse, Http404
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_http_methods
from config.decorators import require_api_key, verify_api_key
from .models import Analytic, Category, MitreTactic, MitreTechnique, Campaign, Snapshot

def serialize_category(category):
    """Serialize an Analytic object to a dictionary."""
    return {
        'id': analytic.id,
        'name': analytic.name,
        'description': analytic.description,
        'status': analytic.status,
        'confidence': analytic.confidence,
        'relevance': analytic.relevance,
        'query': analytic.query,
        'columns': analytic.columns,
        'category': analytic.category.name if getattr(analytic, 'category', None) else None,
        'connector': analytic.connector.name if getattr(analytic, 'connector', None) else None,
        'repo': analytic.repo.name if getattr(analytic, 'repo', None) else None,
        'run_daily': analytic.run_daily,
        'pub_date': analytic.pub_date.isoformat() if getattr(analytic, 'pub_date', None) else None,
    }

@require_api_key('READ')
@require_http_methods(["GET"])
def get_analytics(request):
    """
    Return a list of analytics.
    Allows filtering by status (e.g. ?status=PUB).
    """
    status_filter = request.GET.get('status')
    
    analytics = Analytic.objects.select_related('category', 'connector', 'repo').all()
    if status_filter:
        analytics = analytics.filter(status=status_filter)
        
    data = [serialize_analytic(analytic) for analytic in analytics]
    
    return JsonResponse({'data': data})

@require_http_methods(["GET", "DELETE"])
def get_analytic(request, pk):
    """
    GET: Return details of a specific analytic.
    DELETE: Delete a specific analytic (requires WRITE key).
    """
    perm = 'WRITE' if request.method == 'DELETE' else 'READ'
    error = verify_api_key(request, perm)
    if error:
        return error

    analytic = get_object_or_404(Analytic.objects.select_related('category', 'connector', 'repo'), pk=pk)

    if request.method == 'DELETE':
        analytic.delete()
        return JsonResponse({'status': 'deleted'}, status=200)

    return JsonResponse({'data': serialize_analytic(analytic)})

def serialize_category(category):
    return {
        'id': category.id,
        'name': category.name,
        'short_name': category.short_name,
        'description': category.description,
    }

@require_api_key('READ')
@require_http_methods(["GET"])
def get_categories(request):
    """Return a list of categories."""
    categories = Category.objects.all()
    data = [serialize_category(c) for c in categories]
    return JsonResponse({'data': data})

@require_http_methods(["GET", "DELETE"])
def get_category(request, pk):
    """GET: Return details of a specific category. DELETE: Remove it (WRITE key)."""
    perm = 'WRITE' if request.method == 'DELETE' else 'READ'
    error = verify_api_key(request, perm)
    if error:
        return error

    category = get_object_or_404(Category, pk=pk)

    if request.method == 'DELETE':
        category.delete()
        return JsonResponse({'status': 'deleted'}, status=200)

    return JsonResponse({'data': serialize_category(category)})

def serialize_tactic(tactic):
    return {
        'id': tactic.id,
        'mitre_id': tactic.mitre_id,
        'name': tactic.name,
        'description': tactic.description,
        'position': tactic.position,
    }

@require_api_key('READ')
@require_http_methods(["GET"])
def get_tactics(request):
    """Return a list of Mitre tactics."""
    tactics = MitreTactic.objects.all()
    data = [serialize_tactic(t) for t in tactics]
    return JsonResponse({'data': data})

@require_http_methods(["GET", "DELETE"])
def get_tactic(request, pk):
    """GET: Return details of a specific tactic. DELETE: Remove it (WRITE key)."""
    perm = 'WRITE' if request.method == 'DELETE' else 'READ'
    error = verify_api_key(request, perm)
    if error:
        return error

    tactic = get_object_or_404(MitreTactic, pk=pk)

    if request.method == 'DELETE':
        tactic.delete()
        return JsonResponse({'status': 'deleted'}, status=200)

    return JsonResponse({'data': serialize_tactic(tactic)})

def serialize_technique(technique):
    return {
        'id': technique.id,
        'mitre_id': technique.mitre_id,
        'name': technique.name,
        'is_subtechnique': technique.is_subtechnique,
        'parent_technique_id': technique.mitre_technique_id,
        'description': technique.description,
    }

@require_api_key('READ')
@require_http_methods(["GET"])
def get_techniques(request):
    """Return a list of Mitre techniques."""
    techniques = MitreTechnique.objects.all()
    data = [serialize_technique(t) for t in techniques]
    return JsonResponse({'data': data})

@require_http_methods(["GET", "DELETE"])
def get_technique(request, pk):
    """GET: Return details of a specific technique. DELETE: Remove it (WRITE key)."""
    perm = 'WRITE' if request.method == 'DELETE' else 'READ'
    error = verify_api_key(request, perm)
    if error:
        return error

    technique = get_object_or_404(MitreTechnique, pk=pk)

    if request.method == 'DELETE':
        technique.delete()
        return JsonResponse({'status': 'deleted'}, status=200)

    return JsonResponse({'data': serialize_technique(technique)})

def serialize_campaign(campaign):
    return {
        'id': campaign.id,
        'name': campaign.name,
        'description': campaign.description,
        'date_start': campaign.date_start.isoformat() if campaign.date_start else None,
        'date_end': campaign.date_end.isoformat() if campaign.date_end else None,
        'nb_queries': campaign.nb_queries,
        'nb_analytics': campaign.nb_analytics,
        'nb_endpoints': campaign.nb_endpoints,
    }

@require_api_key('READ')
@require_http_methods(["GET"])
def get_campaigns(request):
    """Return a list of campaigns."""
    campaigns = Campaign.objects.all()
    data = [serialize_campaign(c) for c in campaigns]
    return JsonResponse({'data': data})

@require_http_methods(["GET", "DELETE"])
def get_campaign_detail(request, pk):
    """GET: Return details of a specific campaign. DELETE: Remove it (WRITE key)."""
    perm = 'WRITE' if request.method == 'DELETE' else 'READ'
    error = verify_api_key(request, perm)
    if error:
        return error

    campaign = get_object_or_404(Campaign, pk=pk)

    if request.method == 'DELETE':
        campaign.delete()
        return JsonResponse({'status': 'deleted'}, status=200)

    return JsonResponse({'data': serialize_campaign(campaign)})

def serialize_snapshot(snapshot):
    return {
        'id': snapshot.id,
        'campaign_id': snapshot.campaign_id,
        'analytic_id': snapshot.analytic_id,
        'date': snapshot.date.isoformat() if snapshot.date else None,
        'runtime': snapshot.runtime,
        'hits_count': snapshot.hits_count,
        'hits_endpoints': snapshot.hits_endpoints,
        'anomaly_alert_count': snapshot.anomaly_alert_count,
        'anomaly_alert_endpoints': snapshot.anomaly_alert_endpoints,
    }

@require_api_key('READ')
@require_http_methods(["GET"])
def get_snapshots(request):
    """Return a list of snapshots."""
    snapshots = Snapshot.objects.all()
    data = [serialize_snapshot(s) for s in snapshots]
    return JsonResponse({'data': data})

@require_http_methods(["GET", "DELETE"])
def get_snapshot_detail(request, pk):
    """GET: Return details of a specific snapshot. DELETE: Remove it (WRITE key)."""
    perm = 'WRITE' if request.method == 'DELETE' else 'READ'
    error = verify_api_key(request, perm)
    if error:
        return error

    snapshot = get_object_or_404(Snapshot, pk=pk)

    if request.method == 'DELETE':
        snapshot.delete()
        return JsonResponse({'status': 'deleted'}, status=200)

    return JsonResponse({'data': serialize_snapshot(snapshot)})
