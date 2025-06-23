from bwf_components.plugins.approval.models import ApprovalStatusEnum, FormApproval, ApprovalRecord, ApprovalActionTypesEnum, approval_record_factory
from bwf_components.types import AbstractPluginHandler
from bwf_forms.models import (
    BwfForm
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
        selected_form  = BwfForm.objects.get(id=form.get("id", None))
        form_version = selected_form.active_version

        if not form_version:
            plugin.set_output(False, message="Form version not found")
            return

        approval = FormApproval.objects.create(
            form_version=form_version,
            workflow_instance_id=workflow_instance_id,
            component_instance_id=component_instance_id,
        )
        # send out approval tasks to roles
        print(
            f"http://localhost:9196/bwf_components/approvals/form/{approval.approval_id}/view/"
        )
        plugin.set_on_awaiting_action()
    except BwfForm.DoesNotExist:
        plugin.set_output(False, message="Form not found")
        return


def callback(plugin: AbstractPluginHandler, object_id=None, data={}, user=None):

    approval = FormApproval.objects.filter(approval_id=object_id).first()
    if not approval:
        plugin.set_output(False, message="Approval not found")
        return
    if approval.status != ApprovalStatusEnum.PENDING:
        return
    # validate_roles

    # process the approval response

    first_name = data.get("firstName", "")
    user_email = data.get("email", "")
    action  =  data.get("action", None)

    output_data = {
        "is_approved": False,
    }

    if action == ApprovalActionTypesEnum.APPROVE:
        approval.approve()
        # approval_record_factory(approval, user_email, first_name, action)
        output_data["is_approved"] = True
        plugin.set_output(True, message="Approval granted", data=output_data)
    elif action == ApprovalActionTypesEnum.REJECT:
        approval.reject()
        # approval_record_factory(approval, user_email, first_name, action)
        output_data["is_approved"] = False
        plugin.set_output(True, message="Approval rejected", data=output_data)
    else:
        approval.cancel()
        plugin.set_output(False, message="Unknown action type")


def validate_object(object_id):
    """
    Validate the object ID for the approval.
    """
    return FormApproval.objects.filter(approval_id=object_id).exists()

def can_be_processed(object_id):
    """
    Check if the approval can be processed.
    """
    approval = FormApproval.objects.filter(id=object_id).first()
    if not approval:
        return False
    return approval.status == ApprovalStatusEnum.PENDING