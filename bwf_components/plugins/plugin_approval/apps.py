from django.apps import AppConfig


class BwfModelsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'bwf_components.plugins.plugin_approval'
    verbose_name = "BWF Approval Plugin"
