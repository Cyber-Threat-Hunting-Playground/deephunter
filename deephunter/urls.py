from django.contrib import admin
from django.urls import include, path, re_path
from django.views.generic.base import RedirectView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from .api_router import router as api_router
from . import views

admin.site.login_template = 'custom_admin/login.html'

favicon_view = RedirectView.as_view(url='/static/favicon.ico', permanent=True)
urlpatterns = [
    path('admin/', admin.site.urls),
    path('logout/', views.user_logout, name='user_logout'),
    path('sso/', views.sso, name='sso'),
    path('authorize/', views.authorize, name='authorize'),
    re_path(r'^favicon\.ico$', favicon_view),
    path('', include('dashboard.urls')),
    path('qm/', include('qm.urls')),
    path('extensions/', include('extensions.urls')),
    path('reports/', include('reports.urls')),
    path('connectors/', include('connectors.urls')),
    path('repos/', include('repos.urls')),
    path('notifications/', include('notifications.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('config/', include('config.urls')),

    # Legacy API (read-only, custom ApiKey auth)
    path('api/qm/', include('qm.api_urls')),
    path('api/repos/', include('repos.api_urls')),
    path('api/connectors/', include('connectors.api_urls')),

    # REST API v2 (full CRUD, DRF + Swagger)
    path('api/v2/', include(api_router.urls)),
    path('api/v2/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/v2/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/v2/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
