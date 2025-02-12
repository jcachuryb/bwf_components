import json

from .models import Workflow, WorkflowAction


class WorkFlowController():
    def __init__(self):
        pass


def create_workflow(name, description=None, action=None, env_variables={}):
    workflow =  Workflow.objects.create(name=name, description=description, env_variables=json.dump(env_variables))
    action_name = f"WF{workflow.id}-{name}"
    
    main_action = WorkflowAction.objects.create(name=action_name)
    workflow.main_action = main_action
    return workflow.save()
    

