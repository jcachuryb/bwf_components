from .plugins.base_plugin import PluginWrapperFactory
from bwf_components.workflow.models import Workflow, WorkflowVersion, WorkFlowInstance, WorkflowInstanceFactory, WorkflowComponentInstanceFactory, ComponentInstance, ActionLogRecord

from bwf_components.controller.controller import BWFPluginController

import logging
import uuid
from .utils import process_base_input_definition, get_incoming_values, adjust_workflow_routing

logger = logging.getLogger(__name__)

# Creation Tasks
def create_component_definition_instance(plugin_id, name, route=None, version_number="1", index=0):
    definition: BWFPluginController = BWFPluginController.get_plugin_definition(plugin_id)
    if not definition:
        raise Exception(f"Plugin {plugin_id} not found")
      
    base_input = definition.get("base_input", [])
    base_output = definition.get("base_output", [])
    ui = definition.get("ui", {})
    inputs = []
    outputs = []
    if base_input:
        input_index = 0
        for input_item in base_input:
            inputs.append(process_base_input_definition(input_item, input_index))
            input_index += 1
    
    if base_output:
        output_index = 0
        for output_item in base_output:
            outputs.append({
                'label': output_item.get("label"),
                'key': output_item.get("key"),
                'data_type': output_item.get("type"),
                'data': output_item.get("data", {}),
            })                
            output_index += 1

    instance = {
        "id": str(uuid.uuid4()),
        "name": name,  
        "plugin_id": plugin_id,
        "version_number": version_number,
        "node_type": definition.get("node_type", "node"),
        "ui": {
            "x": index * 200,
            "y": index * 200,
            "class_name": ui.get("icon_class", "bi bi-gear"),
            "icon_image_src": ui.get("icon_image_src", None),
        },
        "config": {
            "inputs": inputs,
            "outputs": outputs,
        },
        "conditions": {
            "is_entry": False,
            "route": None,
        },
    }

    node_definition = node_type_definitions(definition.get("node_type", "node"))
    if node_definition and len(node_definition.keys()) > 0:
        key = list(node_definition.keys())[0]
        instance['config'][key] = node_definition[key]

    return instance


def insert_node_to_workflow(workflow_components, node, data={}):
    route = data.get('route', None)
    node_id = node.get('id', None)
    node_path = data.get('node_path', None)
    parent_node_path = data.get('parent_node_path', None)
    parent_id = data.get('parent_id', None)
    
    if parent_id and parent_node_path:
        parent_node_path_list = parent_node_path.split(".")
        parent_node = None
        for path in parent_node_path_list:
            parent_node = workflow_components.get(path, None)
            if not parent_node:
                raise Exception(f"Parent node {path} not found")

        parent_type = parent_node.get("config", {}).get('node_type', 'node')
        if node_path not in parent_node['config'][parent_type]:
            parent_node['config'][parent_type][node_path] = {}
        is_entry = len(parent_node['config'][parent_type][node_path].keys()) == 0
        parent_node['config'][parent_type][node_path][node_id] = node
        node['config']['path'] = f"{parent_node_path}.{node_path}"
        adjust_workflow_routing(parent_node['config'][parent_type][node_path], node_id, route)
    else:
        node['conditions']['is_entry'] = len(workflow_components.keys()) == 0
        workflow_components[node_id] = node
        node['config']['path'] = f"{node_id}.{node['node_type']}"
        adjust_workflow_routing(workflow_components, node_id, route)


def node_type_definitions(node_type):

    if node_type == 'branch':
        return {
            node_type: {
                'True' : {},
                'False': {},
            }
        }
    elif node_type == 'switch':
        return {
            node_type: {
                'default': {},
            }
        }
    elif node_type == 'loop':
        return {
            node_type: {
                
            }
        }
    elif node_type == 'node':
        return {
            node_type: {
                
            }
        }

# END: Creation Tasks
def list_workflow_nodes(workflow_components):
    components_list = []
    for key, component in workflow_components.items():
        list_item = {
                "id": key,
                "name": component.get("name", "Node"),
                "plugin_id": component.get("plugin_id"),
                "version_number": component.get("version_number", "1"),
                "config": component.get("config", {}),
                "ui": component.get("ui", {}),
                "node_type": component.get("node_type", "node"),
                "conditions": component.get("conditions", {}),
            }
        node_type = component.get("node_type", "node")
        if node_type in ['branch','switch', 'loop']:
            flows = component['config'][node_type].keys()
            list_item['children'] = []
            for flow in flows:
                list_item['children'].append({
                    'name': flow,
                    'children': list_workflow_nodes(component['config'][node_type][flow])
                })
        components_list.append(list_item)
    return components_list