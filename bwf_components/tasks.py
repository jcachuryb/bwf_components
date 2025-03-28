from bwf_components.action_log import tasks as action_log_tasks
from bwf_components.components.plugins.base_plugin import PluginWrapperFactory
from bwf_components.components.models import WorkflowComponent, FailureHandleTypesEnum
from bwf_components.components.dto.component_dto import ComponentDto
from bwf_components.controller.controller import BWFPluginController
from bwf_components.workflow.models import Workflow, WorkflowVersion, WorkFlowInstance, WorkflowInstanceFactory, WorkflowComponentInstanceFactory, ComponentInstance, ActionLogRecord
from bwf_components import exceptions as bwf_exceptions
import logging
import time
logger = logging.getLogger(__name__)


def start_workflow(workflow_id, payload={}):
    instance = None
    try:
        workflow = Workflow.objects.get(id=workflow_id)
        workflow_version = workflow.get_active_version()
        if not workflow_version:
            raise Exception("Workflow doesn't have an active version")
        instance = WorkflowInstanceFactory.create_instance(workflow_version, payload)
        register_workflow_step(instance)       
        return instance
    except Exception as e:
        if instance:
            instance.set_status_error(str(e))
        raise e


def register_workflow_step(workflow_instance: WorkFlowInstance, step=None, output_prev_component={}):
    try:
        definition = workflow_instance.get_json_definition()
        components = definition.get("workflow", {})
        step_component = None
        if step:
            step_component = components.get(step, None)
        else:
            for key, component in components.items():
                if component['conditions'].get('is_entry', False):
                    step_component = component
                    break
            if step_component is None:
                err = "Workflow doesn't have an entry point"
                workflow_instance.set_status_error(err)
                raise Exception(err)
            
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

def start_pending_component(current_component: ComponentInstance, parent=None):
    workflow_instance = current_component.workflow
    try:
        current_component.set_status_running()
        controller = BWFPluginController.get_instance()
        plugin_module = controller.get_plugin_module(current_component.plugin_id, current_component.plugin_version)
        if not plugin_module:
            err = f"Plugin {current_component.plugin_id} not found"
            current_component.set_status_error(err)
            workflow_instance.set_status_error(err)
            return
        
        # TODO: Get Global variables
        # get secrets and globals
        # node | loop | branch | switch
        plugin_wrapper_class = PluginWrapperFactory.wrapper("node")
        plugin_wrapper_instance = plugin_wrapper_class(current_component, workflow_instance, context={
                                                    "variables": current_component.workflow.variables.get("variables", {}),
                                                    "inputs": current_component.workflow.variables.get("inputs", {}),
                                                    "incoming": current_component.input.get("incoming", {})
                                                })
        try:
            # calls execute but should call any method that is defined in the plugin that receives a plugin_wrapper_instance
            plugin_module.execute(plugin_wrapper_instance)
        except Exception as e:
            logger.error(f"Error while executing component {current_component.id}")
            logger.error(e)
            if plugin_wrapper_instance:
                plugin_wrapper_instance.on_failure(e)
    except Exception as e:
        logger.error(f"Error while starting pending component {current_component.id}")
        logger.error(e)
        current_component.set_status_error(str(e))


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
