from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView
from rest_framework.schemas import get_schema_view

from library_project import settings as project_settings

schema_view = get_schema_view(
    title=project_settings.API_DOCUMENTATION["TITLE"],
    description=project_settings.API_DOCUMENTATION["DESCRIPTION"],
    version=project_settings.API_DOCUMENTATION["VERSION"],
    public=True,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("catalog.urls")),
    path("api/schema/", schema_view, name="api-schema"),
    path(
        "api/docs/",
        TemplateView.as_view(
            template_name="swagger-ui.html",
            extra_context={"schema_url": "api-schema"},
        ),
        name="swagger-ui",
    ),
]
