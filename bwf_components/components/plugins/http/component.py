import requests
import json

from bwf_components.components.plugins.base_plugin import BasePlugin
from bwf_components.exceptions import ComponentExecutionException


def execute(plugin:BasePlugin):
    # plugin = BasePlugin(component_instance, workflow_instance, context) # Wrapper
    inputs = plugin.collect_context_data()
    component_input = inputs['input']
    url = component_input.get("url")
    method = component_input.get("method", "GET")
    headers = component_input.get("headers", {})
    body = component_input.get("body", {})
    try:
        response = requests.request(method, url, headers=headers, data=body)
        output = {
            "status": response.status_code,
            "body": {}
        }
        output["body"] = json.loads(response.text)
        plugin.set_output(True, data=output)
    except Exception as e:
        raise ComponentExecutionException(str(e), plugin.component.component_id)
