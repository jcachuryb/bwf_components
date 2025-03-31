
from bwf_components.workflow.models import WorkFlowInstance, ComponentInstance
from bwf_components.components.plugins.base_plugin import BranchPlugin
from bwf_components.components.plugin_utils.emails import email_sender


def execute(component_instance:ComponentInstance, workflow_instance: WorkFlowInstance, context={}):
    plugin = BranchPlugin(component_instance, workflow_instance, context) # Wrapper
    
    inputs = plugin.collect_context_data()
    component_input = inputs['input']
    
    from_email = component_input.get("from")
    to = component_input.get("to")
    subject = component_input.get("subject")
    body = component_input.get("body")
    email_sender.send_static_email(from_email, to, subject, body)
    plugin.set_output(True)
    return True
