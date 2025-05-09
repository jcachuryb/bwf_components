from django.apps import AppConfig


class BwfModelsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'bwf_components.plugins.approval'
    label = 'bwf_approvals'
    verbose_name = "BWF Approval Plugin"
