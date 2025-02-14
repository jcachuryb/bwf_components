
from actions.base_action import BaseComponentAction
from action_utils.emails import email_sender


class AssignValueAction(BaseComponentAction):


    def execute(self):
        inputs = self.collect_inputs()
        component_input = inputs['input']
        
        input = component_input['input']
        key = input.get("local_variable_key")

        self.workflow_instance.variables['local'][key] = input['value']
        return True

