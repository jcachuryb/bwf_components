import requests
import json

from bwf_components.workflow.models import WorkFlowInstance, ComponentInstance
from bwf_components.components.plugins.base_plugin import BasePlugin


def execute(plugin:BasePlugin):
    # plugin = BasePlugin(component_instance, workflow_instance, context) # Wrapper
    inputs = plugin.collect_context_data()
    component_input = inputs['input']
    url = component_input.get("url")
    method = component_input.get("method", "GET")
    headers = component_input.get("headers", {})
    body = json.load(component_input.get("body"))
    response = requests.request(method, url, headers=headers, data=body)
    plugin.set_output(True, data={"response": {"status_code": response.status_code, "body": json.loads(response.text)}})
    
    plugin.call_next_node()

