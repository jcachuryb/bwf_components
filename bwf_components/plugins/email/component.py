from bwf_components.plugin_utils.emails import email_sender

from bwf_components.types import AbstractPluginHandler

def execute(plugin:AbstractPluginHandler):
    inputs = plugin.collect_context_data()
    component_input = inputs['input']
    
    from_email = component_input.get("from")
    to = component_input.get("to")
    subject = component_input.get("subject")
    body = component_input.get("body")
    try:
        email_sender.send_static_email(from_email, to, subject, body)
        plugin.set_output(True)
    except Exception as e:
        plugin.set_output(False, message=str(e))

