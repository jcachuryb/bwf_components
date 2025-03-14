
class ComponentDto:
    def __init__(self, id, name, plugin_id, version_number, config, conditions, workflow_context={}):
        self.id = id
        self.name = name
        self.plugin_id = plugin_id
        self.version_number = version_number
        self.inputs = None
        self.outputs = None
        self.config = config
        self.conditions = conditions
        self.workflow_context = workflow_context
    
    def get_inputs(self):
        if not self.inputs:
            self.__eval_inputs(self.workflow_context)
        return self.inputs
    
    def __eval_inputs(self, workflow_context={}):
        component_inputs = self.config['inputs']
        for input in component_inputs:
            new_input = {
                "key": input['key'],
                "value": None,
            }
            if input['value']['is_expression']:
                expression = input['value']['value']
                eval(self.expression, None, {"context": workflow_context})
                pass
            elif input['value']['value_ref']:
                pass
            elif input['value']['value']:
                pass
            self.inputs[new_input['key']] = new_input['value']