from bwf_components.plugins.approval.models import FormApproval, ApprovalRecord
from bwf_components.types import AbstractPluginHandler
from bwf_components.bwf_forms.models import (
    BwfFormVersion,
)

def execute(plugin: AbstractPluginHandler):
    inputs = plugin.collect_context_data()
    workflow_instance_id = plugin.workflow_instance_id()
    component_instance_id = plugin.component_instance_id()

    component_input = inputs["input"]
    roles = component_input.get("roles", [])
    form = component_input.get("form", None)
    approval_timeout = component_input.get("approval_timeout", 300)
    # TODO: Specify way of distribution of task to roles
    ids = []
    for role in roles:
        if "role_id" in role:
            id = role.get("role_id", None).get("id", None)
        elif "id" in role:
            id = role.get("id", None)
        else:
            id = role
        ids.append(id)

    try:
        form_version = BwfFormVersion.objects.get(id=form.get("id", None))

        approval = FormApproval.objects.create(
            form_version=form_version,
            workflow_instance_id=workflow_instance_id,
            component_instance_id=component_instance_id,
        )
        # send out approval tasks to roles
        print(
            f"http://localhost:9196/bwf_components/approvals/form/{approval.approval_id}/view/"
        )
    except BwfFormVersion.DoesNotExist:
        plugin.set_output(False, message="Form or form version not found")
        return


def callback(plugin: AbstractPluginHandler, data={}):

    pass
