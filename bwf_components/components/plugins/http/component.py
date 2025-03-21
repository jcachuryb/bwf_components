import requests
import json
import logging
from bwf_components.components.plugins.base_plugin import BasePlugin
logger = logging.getLogger(__name__)

def execute(plugin:BasePlugin):
    # plugin = BasePlugin(component_instance, workflow_instance, context) # Wrapper
    inputs = plugin.collect_context_data()
    component_input = inputs['input']
    url = component_input.get("url")
    method = component_input.get("method", "GET")
    headers = component_input.get("headers", {})
    body = component_input.get("body", {})
    response = requests.request(method, url, headers=headers, data=body)
    output = {
        "status": response.status_code,
        "body": {}
    }
    try:
        output["body"] = json.loads(response.text)
        plugin.set_output(True, data=output)
    except Exception as e:
        plugin.set_output(False, message=str(e), data=output)
        logger.error(f"Error in HTTP Plugin: {str(e)}")
