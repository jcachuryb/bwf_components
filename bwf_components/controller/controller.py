import os
import json
from bwf_components import settings_bwf as settings
from bwf_components.workflow.models import ComponentInstance, ComponentStepStatusEnum
from importlib.machinery import SourceFileLoader


BASE_PLUGIN_ROUTE = os.path.join(settings.BASE_DIR, 'bwf_components', 'components', 'plugins')

class BWFPluginController:
    _instance = None

    @staticmethod
    def get_instance():
        if BWFPluginController._instance is None:
            BWFPluginController._instance = BWFPluginController()
        return BWFPluginController._instance
    
    
    def __init__(self):
        self.plugins = {}
        self.load_plugins()
    
    def load_plugins(self):
        for plugin in os.listdir(BASE_PLUGIN_ROUTE):
            plugin_path = os.path.join(BASE_PLUGIN_ROUTE, plugin)
            if os.path.isdir(plugin_path):
                try:
                    new_plugin = self.__load_bwf_plugin(plugin_path)
                    if not new_plugin:
                        continue
                    
                    new_plugin.get("settings")
                    self.plugins[new_plugin.get('id')] = new_plugin
                except Exception as e:
                    print(f"Error loading plugin {plugin}: {e}")

    
    def __load_bwf_plugin(self, plugin_path):
        definition_json = os.path.join(plugin_path, 'definition.json')
        if not os.path.exists(definition_json):
            raise Exception(f"Plugin {plugin_path} does not have a definition.json file")
        
        
        plugin_definition = None
        with open(definition_json) as json_file:
            plugin_definition = json.load(json_file)
        
        
        # definition_module = SourceFileLoader("definition", definitions_path).load_module()
        # function_to_call = 'get_definition'

        # if not hasattr(definition_module, function_to_call):
        #     raise Exception(f"Plugin {plugin_path} does not have a '{function_to_call}' function in the definition.py file")
           
        new_plugin = {'id': plugin_definition.get('id'),
                      'name': plugin_definition.get('name'),
                      'version': plugin_definition.get('version'),
                      'description': plugin_definition.get('description'),
                      'plugin_path': plugin_path,
                      'icon_class': plugin_definition.get('icon_class'),
                    }
        # TODO: Validate it has all required fields
              
        return new_plugin

    def get_plugins_list(self):
        return list(self.plugins.values())
    
    def get_plugin_definition(self, plugin_id):
        plugin = self.plugins.get(plugin_id, None)
        if plugin:
            plugin_path = plugin.get('plugin_path')
            definition_json = os.path.join(plugin_path, 'definition.json')
            plugin_definition = None
            with open(definition_json) as json_file:
                plugin_definition = json.load(json_file)

            base_inputs  = plugin_definition.get('base_input')
            base_outputs = plugin_definition.get('base_output')

            return {
                'id': plugin_definition.get('id'),
                'version': plugin_definition.get('version'),
                'name': plugin_definition.get('name'),
                'description': plugin_definition.get('description'),
                'base_input': base_inputs,
                'base_output': base_outputs
            }                
        return None

    def get_plugin_module(self, plugin_id):
        plugin = self.plugins.get(plugin_id, None)
        if plugin:
            plugin_path = plugin.get('plugin_path')
            component_path = os.path.join(plugin_path, 'component.py')
            component_module = SourceFileLoader("component", component_path).load_module()
            return component_module
        return None