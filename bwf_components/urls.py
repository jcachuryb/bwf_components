"""
URL configuration for layerCacheService project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django import conf
from django import urls
from . import views
from .workflow import views as workflow_viewsets
from .components import views as component_viewsets
from rest_framework import routers

admin.site.site_header = conf.settings.PROJECT_TITLE
admin.site.index_title = conf.settings.PROJECT_TITLE
admin.site.site_title = conf.settings.PROJECT_TITLE

router = routers.SimpleRouter()
router.register(r'api/workflow', workflow_viewsets.WorkflowViewset)

urlpatterns = router.urls

urlpatterns += [
    path('bwf_admin/', admin.site.urls),
    path('dashboard', views.HomeView.as_view(), name='home'),
    path('workflow/<int:workflow_id>/', views.WorkflowView.as_view(), name='workflow'),
    path('api/definitions/', component_viewsets.ComponentDefinitionViewset.as_view()),

]
