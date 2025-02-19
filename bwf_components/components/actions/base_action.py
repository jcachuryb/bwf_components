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
        self.context = context

        # output

    
    def execute(self):
        raise Exception("Need to implement the execute method")

    def set_output(self, success:bool, message="", data={}):
        # Call workflow coordinator to set the output and call the next node
        # store result in workspace instance context
        self.component.output = {
            "success": success,
            "message": message,
            "data": data
        }
        self.component.save()
    

    def collect_context_data(self):
        context = self.context | {
            "input": {},
        }
        for key, value in self.component.input.items():
            context["input"][key] = value["value"]
        return context