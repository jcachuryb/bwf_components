from bwf_components.components.models import WorkflowComponent
from bwf_components.workflow.models import WorkFlowInstance, ComponentInstance

""" 
component: WorkflowComponent
        


context: Dict 
        - global
        - local
        - cluster
        - output

 """


class BaseComponentAction:
    
    def __init__(self, component_instance:ComponentInstance, workflow_instance: WorkFlowInstance, context={}):
        self.component = component_instance
        self.base_component = component_instance.component
        self.workflow_instance = workflow_instance
        self.context = context | component_instance.input

        # output

    
    def execute(self):
        raise Exception("Need to implement the execute method")

    def set_output(self, value={}):
        # Call workflow coordinator to set the output and call the next node
        # store result in workspace instance context
        output = {"component_id": self.component, "output": value}
        print(vars(output))
        pass
    

    def collect_inputs(self):
        input = self.workflow_instance.variables
        calculated_fields = self.component.get_input_values(context)
        context = self.context['variables'] | {
            "global": input['global'],
            "local": input['local'],
            "input": calculated_fields,
        }
        return context