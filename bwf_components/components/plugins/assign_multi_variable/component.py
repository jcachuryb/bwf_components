import logging
from bwf_components.workflow.models import WorkFlowInstance, ComponentInstance
from bwf_components.components.plugins.base_plugin import BasePlugin
logger = logging.getLogger(__name__)

def execute(plugin:BasePlugin):
    inputs = plugin.collect_context_data()
    component_input = inputs['input']
    multi_variables = component_input.get("variables", [])
    try:
        for variable in multi_variables:
            key = variable.get("local_variable_key")
            value = variable.get("value")
            plugin.update_workflow_variable(key, value)
        plugin.set_output(True)
    except Exception as e:
        plugin.set_output(False, message=str(e))
        logger.error(f"Error in Assign Multi Variable Plugin: {str(e)}")
    