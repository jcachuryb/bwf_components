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
from django.urls import path
from django import conf
from bwf_components.plugins.approval import views as model_views

urlpatterns = [
    path('roles/', model_views.BWF_RoleListView.as_view()),
    path('approval-forms/', model_views.BWF_ApprovalFormListView.as_view()),
    path('form/<str:form_approval_id>/view/', model_views.ApprovalFormVisualizerView.as_view(), name='approval_form_view'),
    path('form/<str:form_approval_id>/definition/', model_views.form_definition, name='form_definition'),
    
]
