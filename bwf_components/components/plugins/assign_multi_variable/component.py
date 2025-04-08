import logging
from bwf_components.workflow.models import WorkFlowInstance, ComponentInstance
from bwf_components.components.plugins.base_plugin import BasePlugin
from bwf_components.exceptions import ComponentExecutionException

def execute(plugin:BasePlugin):
    inputs = plugin.collect_context_data()
    component_input = inputs['input']
    multi_variables = component_input.get("variables", [])
    if not multi_variables:
        multi_variables = []
    try:
        for variable in multi_variables:
            key = variable.get("local_variable_key")
            value = variable.get("value")
            plugin.update_workflow_variable(key, value)
        plugin.set_output(True)
    except Exception as e:
        raise ComponentExecutionException(str(e), plugin.component.component_id)
    