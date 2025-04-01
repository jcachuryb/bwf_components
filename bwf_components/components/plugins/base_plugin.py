from bwf_components.workflow.models import WorkFlowInstance, ComponentInstance

""" 
component: WorkflowComponent
        


context: Dict 
        - global
        - local
        - output

 """


class BasePlugin:
    
    def __init__(self, component_instance:ComponentInstance, workflow_instance: WorkFlowInstance, context={}):
        self.type = "node"
        self.component = component_instance
        self.workflow_instance = workflow_instance
        self.context = context

        # output

    def set_plugin_component(self, executableComponent):
        # self.component = executableComponent
        pass
    
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
        if success:
            self.on_complete()
        else:
            self.on_failure(message)

    def call_next_node(self):
        from bwf_components.tasks import register_workflow_step

        workflow_definition = self.workflow_instance.get_json_definition()
        current_definition = None
        wf_components = workflow_definition.get("workflow", {})
        for key, value in wf_components.items():
            if key == self.component.component_id:
                current_definition = value
                break
        if not current_definition:
            raise Exception(f"Component {self.component.component_id} not found in workflow definition")
        next_component_id = current_definition.get("conditions", {}).get("route", None)
        if next_component_id:
            register_workflow_step(self.workflow_instance, step=next_component_id, output_prev_component=self.component.output.get("data", {}))
        else:
            self.workflow_instance.set_status_completed()

    def on_complete(self):
        self.component.set_status_completed()
        self.call_next_node()
    
    def on_failure(self, error={}):
        # TODO: Call process on Failure
        self.component.set_status_error(error)
        self.workflow_instance.set_status_error(error)

    def collect_context_data(self):
        context = self.context | {
            "input": self.component.input,
        }
        return context

    def update_workflow_variable(self, id, value):
        workflow_variables = self.workflow_instance.get_json_definition().get('variables')
        variable = None
        for var_key in workflow_variables:
            if workflow_variables[var_key].get('id') == id:
                variable = workflow_variables[var_key]
                break

        self.workflow_instance.variables['variables'][variable['id']] = value
        self.workflow_instance.variables['variables'][variable['key']] = value
        self.workflow_instance.save()



class NodePlugin(BasePlugin):
    pass

class AyncNodePlugin(BasePlugin):
    def __init__(self, component_instance:ComponentInstance, workflow_instance: WorkFlowInstance, context={}):
        super().__init__(component_instance, workflow_instance, context)
        self.type = "async-node"
        self.component = component_instance
        self.workflow_instance = workflow_instance
        self.context = context
    
    def on_continue_task(self):
        pass

    def on_awaiting_action(self):
        self.component.set_status_awaiting_action()
        pass


class LoopPlugin(BasePlugin):

    def __init__(self, component_instance:ComponentInstance, workflow_instance: WorkFlowInstance, context={}):
        super().__init__(component_instance, workflow_instance, context)
        self.type = "loop"
        self.loop = self.component['config'].get("loop", {})
        self.loop_variable = self.loop.get("variable")
        self.loop_range = self.loop.get("range")
        self.loop_step = self.loop.get("step")
        self.loop_condition = self.loop.get("condition")
        self.loop_index = 0

    def execute(self):

        return super().execute()


class BranchPlugin(BasePlugin):
    def __init__(self, component_instance:ComponentInstance, workflow_instance: WorkFlowInstance, context={}):
        super().__init__(component_instance, workflow_instance, context)
        self.type = "branch"
        self.branches = self.component['config'].get("branch", {})
        self.branch_index = 0



    def on_complete(self):
        return super().on_complete()
class SwitchPlugin(BasePlugin):
    def __init__(self, component_instance, workflow_instance, context={}):
        super().__init__(component_instance, workflow_instance, context)
        self.type = "switch"
        self.switch = self.component['config'].get("switch", {})
        self.switch_variable = self.switch.get("variable")
        self.switch_cases = self.switch.get("cases", {})
        self.switch_default = self.switch.get("default")
        self.switch_index = 0





class PluginWrapperFactory:
    @staticmethod
    def wrapper(plugin_type="node"):
        if plugin_type == "node":
            return NodePlugin
        if plugin_type == "async-node":
            return AyncNodePlugin
        if plugin_type == "loop":
            return LoopPlugin
        if plugin_type == "branch":
            return BranchPlugin
        if plugin_type == "switch":
            return SwitchPlugin
        return BasePlugin