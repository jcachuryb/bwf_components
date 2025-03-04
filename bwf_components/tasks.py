import json
from bwf_components.workflow.models import Workflow, WorkFlowInstance, WorkflowInstanceFactory, WorkflowComponentInstanceFactory, ComponentInstance, ActionLogRecord
from bwf_components.components.models import WorkflowComponent, FailureHandleTypesEnum
from bwf_components.controller.controller import BWFPluginController

import logging
import time
logger = logging.getLogger(__name__)


def start_workflow(workflow_id, payload={}):
    instance = None
    try:
        workflow = Workflow.objects.get(id=workflow_id)
        instance = WorkflowInstanceFactory.create_instance(workflow, payload)
        register_workflow_step(instance)       
        return instance
    except Exception as e:
        if instance:
            instance.set_status_error(str(e))
        raise e


def register_workflow_step(workflow_instance: WorkFlowInstance, step=0, output_prev_component={}):
    try:
        workflow = workflow_instance.workflow
        step_component = workflow.main_cluster.components.filter(step__index__gt=step).order_by("step__index").prefetch_related("input").first()
        if step_component is None:
            workflow_instance.set_status_completed()
            return
        input_params = workflow_instance.variables
        input_params['incoming'] = output_prev_component
        component_instance = WorkflowComponentInstanceFactory.create_component_instance(workflow_instance, step_component, input_params)
        if component_instance is None:
            workflow_instance.set_status_error(f"Component instance could not be created. Step: {step} {step_component}" )
            raise Exception("Component instance could not be created")
        # register in queue
        return workflow_instance
    except Exception as e:
        logger.error(e)
        workflow_instance.set_status_error(str(e))
    return None

def start_pending_component(current_component: ComponentInstance):
    base_component = current_component.component
    workflow_instance = current_component.workflow
    try:
        current_component.set_status_running()
        controller = BWFPluginController.get_instance()
        plugin_module = controller.get_plugin_module(base_component.plugin_id)
        if not plugin_module:
            current_component.set_status_error("Plugin not found")
            workflow_instance.set_status_error("Plugin not found")
            raise Exception("Component instance could not be created")
        
        # TODO: Get Global variables
        # get secrets and globals
        plugin_instance = plugin_module.execute(component_instance=current_component, workflow_instance=current_component.workflow, context={
            "global": {},
            "local": current_component.workflow.variables.get("local", {}),
            "inputs": current_component.workflow.variables.get("inputs", {}),
        })
        
        output = plugin_instance.output
        if not output.get("success", False):
            initiate_fallback_component_action(current_component)
        else:
            current_component.set_status_completed()
            register_workflow_step(current_component.workflow, current_component.component.step.index, output.get("data", {}))
    except Exception as e:
        logger.error(f"Error while executing component {current_component.id}")
        logger.error(e)
        initiate_fallback_component_action(current_component)


def initiate_fallback_component_action(current_component: ComponentInstance):
    base_component = current_component.component
    output = current_component.output if current_component.output else {}
    if hasattr(base_component, "on_fail"):
        fallback = base_component.on_fail
        if fallback.type == FailureHandleTypesEnum.RETRY:
            if fallback.num_retries < fallback.max_retries:
                time.sleep(max(fallback.get_retry_interval_in_seconds(), 5))
                fallback.num_retries += 1
                fallback.save()
                return start_pending_component(current_component)
            else:
                current_component.set_status_error("Max retries reached")
                # for now, we finish the workflow, but if this is a subworkflow, we can handle it differently
                current_component.workflow.set_status_error(output.get("message", "Error while executing component"))

                return None
        if fallback.type == FailureHandleTypesEnum.TERMINATE:
            current_component.set_status_error(output.get("message", "Error while executing component"))
            # for now, we finish the workflow, but if this is a subworkflow, we can handle it differently
            current_component.workflow.set_status_error(output.get("message", "Error while executing component"))
            return
        if fallback.type == FailureHandleTypesEnum.IGNORE:
            current_component.set_status_error("Skipped error while executing component")
            register_workflow_step(current_component.workflow, current_component.component.step.index, output.get("data", {}))
            return
        if fallback.type == FailureHandleTypesEnum.CUSTOM:
            pass
    else:
        current_component.set_status_error(output.get("message", "Error while executing component"))
        # for now, we finish the workflow, but if this is a subworkflow, we can handle it differently
        current_component.workflow.set_status_error(output.get("message", "Error while executing component"))
        return None
