from .plugins.base_plugin import PluginWrapperFactory
from bwf_components.workflow.models import Workflow, WorkflowVersion, WorkFlowInstance, WorkflowInstanceFactory, WorkflowComponentInstanceFactory, ComponentInstance, ActionLogRecord

from bwf_components.controller.controller import BWFPluginController

import logging
import uuid
from .utils import process_base_input_definition, get_incoming_values, adjust_workflow_routing

logger = logging.getLogger(__name__)

def extract_workflow_mapping(workflow_components, workflow_mapping={}):
    for p_key, parent_component in workflow_components.items():
        workflow_mapping[p_key] = {
            'id': p_key,
            'path': parent_component.get('config', {}).get('path', None),
            'plugin_id': parent_component.get('plugin_id', None),
            'version_number': parent_component.get('version_number', None),
        }
        node_type = parent_component.get('node_type', 'node')
        if node_type != 'node':
            for flow_key, flow in parent_component['config'][node_type].items():
                extract_workflow_mapping(flow, workflow_mapping)

def find_component_in_tree(workflow_definition, component_id):
    workflow_components = workflow_definition.get('workflow', {})
    mapping = workflow_definition['mapping'].get(component_id, None)
    if not mapping or not mapping.get('path', None):
        raise Exception(f"Component {component_id} not found in mapping")
    path = mapping.get('path', None)
    path_list = path.split('.')
    if len(path_list) == 0:
        raise Exception(f"Component {component_id} not found in mapping")
    component = None
    path_length = len(path_list)
    for i in range(0, path_length):
        path = path_list[i]
        component = workflow_components.get(path, None) if i == 0 else component.get(path, None)
        if not component:
            raise Exception(f"Component {component_id} not found in mapping")
    return component

def get_encasing_flow(workflow_definition, component_id):
    workflow_components = workflow_definition.get('workflow', {})
    mapping = workflow_definition['mapping'].get(component_id, None)
    if not mapping or not mapping.get('path', None):
        raise Exception(f"Component {component_id} not found in mapping")
    path = mapping.get('path', None)
    path_list = path.split('.')
    if len(path_list) == 0:
        raise Exception(f"Component {component_id} not found in mapping")
    
    encasing_flow = workflow_components
    path_length = len(path_list) - 1
    for i in range(0, path_length):
        path = path_list[i]
        encasing_flow = encasing_flow.get(path, None)
        if not encasing_flow:
            raise Exception(f"Component {component_id} not found in mapping")
    return encasing_flow


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


def insert_node_to_workflow(workflow_definition, node, data={}):
    workflow_components = workflow_definition.get('workflow', {})
    route = data.get('route', None)
    node_id = node.get('id', None)
    node_path = data.get('node_path', None)
    parent_node_path = data.get('parent_node_path', None)
    parent_id = data.get('parent_id', None)
    is_entry = data.get('is_entry', False)
    flow = workflow_components
    if parent_id and parent_node_path:
        parent_node_path_list = parent_node_path.split(".")
        if len(parent_node_path_list) == 0:
            raise Exception("Parent node path is empty")
        
        for i in range(0, len(parent_node_path_list)):
            path = parent_node_path_list[i]
            if i == 0:
                parent_node = workflow_components.get(path, None)
            else:
                parent_node = parent_node.get(path, None)
            if not parent_node:
                raise Exception(f"Parent node {path} not found")

        parent_type = parent_node.get('node_type', 'node')
        if node_path not in parent_node['config'][parent_type]:
            parent_node['config'][parent_type][node_path] = {}

        flow = parent_node['config'][parent_type][node_path]
        is_entry = is_entry or len(parent_node['config'][parent_type][node_path].keys()) == 0
        node['conditions']['is_entry'] = is_entry
        parent_node['config'][parent_type][node_path][node_id] = node
        node['config']['path'] = f"{parent_node_path}.config.{parent_type}.{node_path}.{node_id}"
        adjust_workflow_routing(parent_node['config'][parent_type][node_path], node_id, route)                    
    else:
        is_entry = is_entry or len(workflow_components.keys()) == 0
        node['conditions']['is_entry'] = is_entry
        workflow_components[node_id] = node
        node['config']['path'] = f"{node_id}"
        adjust_workflow_routing(workflow_components, node_id, route)
    
    if is_entry:
        for key, value in flow.items():
            if key != node_id:
                value['conditions']['is_entry'] = False
                adjust_workflow_routing(flow, key, node_id)

    workflow_definition['mapping'][node['id']] = {
        'id': node['id'],
        'path': node['config']['path'] ,
        'plugin_id': node['plugin_id'],
        'version_number': node['version_number'],
    }
        
    return node


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
def to_ui_workflow_node(component, parent_info={}):
    
    workflow_node = {
            "id": component.get("id", None),
            "name": component.get("name", "Node"),
            "plugin_id": component.get("plugin_id"),
            "version_number": component.get("version_number", "1"),
            "config": component.get("config", {}),
            "ui": component.get("ui", {}),
            "node_type": component.get("node_type", "node"),
            "conditions": component.get("conditions", {}),
            "parent_info": parent_info,
        }
    node_type = component.get("node_type", "node")
    if node_type in ['branch','switch', 'loop']:
        flows = component['config'][node_type].keys()
        path_info = {
            'parent_id': component['id'],
            'parent_node_path': component['config']['path'],
            'node_path': '',
        }
        for flow in flows:
            path_info['node_path'] = flow
            component['config'][node_type][flow] = list_workflow_nodes(component['config'][node_type][flow], path_info)
    
    return workflow_node

def list_workflow_nodes(workflow_components, parent_info={}):
    components_list = []
    for key, component in workflow_components.items():
        list_item = to_ui_workflow_node(component, parent_info)
        components_list.append(list_item)
    return components_list