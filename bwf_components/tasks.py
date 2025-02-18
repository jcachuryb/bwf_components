import json
from bwf_components.workflow.models import Workflow, WorkFlowInstance, WorkflowInstanceFactory, WorkflowComponentInstanceFactory, ComponentInstance
from bwf_components.components.models import WorkflowComponent



def start_workflow(workflow_id, payload={}):
    instance = None
    try:
        workflow = Workflow.objects.get(id=workflow_id)
        instance = WorkflowInstanceFactory.create_instance(workflow, payload)
        main_flow_component = workflow.main_cluster.components.all().order_by("step__index").prefetch_related("input").first()
        if main_flow_component is None:
            instance.set_status_completed()
            return instance
        component_instance = WorkflowComponentInstanceFactory.create_component_instance(instance, main_flow_component, instance.variables)
        if component_instance is None:
            raise Exception("Component instance could not be created")
        # register in queue
        return instance
    except Exception as e:
        if instance:
            instance.set_status_error(str(e))
        raise e

def start_pending_component(current_component: ComponentInstance):
    base_component = current_component.component
    try:
        current_component.set_status_running()
        # get secrets and globals
        task_class = base_component.get_component_class()
        instance = task_class(component=current_component, workflow_instance=current_component.workflow, context={})
        if not instance.execute():
            # execute fallback action
            pass
        else:
            current_component.set_status_completed()
    except Exception as e:
        current_component.set_status_error(str(e))
        return None
    return instance