from bwf_components.bwf_models.models import BWF_Role
from bwf_components.types import AbstractPluginHandler

def execute(plugin:AbstractPluginHandler):
    inputs = plugin.collect_context_data()
    component_input = inputs['input']
    
    try:
        # email_sender.send_static_email(from_email, to, subject, body)
        plugin.set_output(True)
    except Exception as e:
        plugin.set_output(False, message=str(e))

def callback(plugin:AbstractPluginHandler, data={}):
    pass
