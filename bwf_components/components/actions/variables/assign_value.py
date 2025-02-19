
from bwf_components.components.actions.base_action import BaseComponentAction
from bwf_components.components.action_utils.emails import email_sender


class AssignValueAction(BaseComponentAction):


    def execute(self):
        context = self.collect_context_data()
        component_input = context['input']
        
        key = component_input.get("local_variable_key")

        self.workflow_instance.variables['local'][key] = component_input.get("value")
        self.workflow_instance.save()
        self.set_output(True)
        return True

