from bwf_components.components.models import WorkflowComponent
from bwf_components.workflow.models import WorkFlowInstance

""" 
component: WorkflowComponent
        


context: Dict 
        - global
        - local
        - cluster
        - output

 """


class BaseComponentAction:
    
    def __init__(self, component:WorkflowComponent, workflow_instance: WorkFlowInstance, context={}):
        self.component = component
        self.workflow_instance = workflow_instance
        self.context = context

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
        context = self.context['variables'] | {
            "input": input,
        }
        calculated_fields = self.component.get_input_values(context)
        return calculated_fields