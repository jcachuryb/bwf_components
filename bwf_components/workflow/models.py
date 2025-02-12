import uuid

from django.db import models, transaction
from django.conf import settings
from django.core.files.storage import FileSystemStorage

from components.models import ComponentDefinition


upload_storage = FileSystemStorage(location=settings.PRIVATE_MEDIA_ROOT)

WORKFLOW_STATUS = [
    ("PENDING", "initial"),
    ("RUNNING", "running"),
    ("COMPLETED", "completed"),
    ("ERROR", "error")
]

ACTION_STATUS = [
    ("PENDING", "initial"),
    ("RUNNING", "running"),
    ("COMPLETED", "completed"),
    ("ERROR", "error")
]


WORKFLOW_INPUT_TYPES = [
    ("STRING", "string"),
    ("NUMBER", "number"),
    ("ARRAY", "array"),
    ("OBJECT", "object"),
    ("BOOLEAN", "boolean"),
    ("SELECT", "select"),
    ("MULTI_SELECT", "multi_select"),
    ("FILE", "file"),
    ("ANY", "any"),
]

def get_unique_id():
    return str(uuid.uuid4())

def upload_to_path(instance, filename):
    return f"workflows/{instance.id}/{instance.current_active_version}"

# TODO: Context Class

class WorkflowInput(models.Model):
    label = models.CharField(max_length=100)
    key = models.CharField(max_length=100)
    description = models.CharField(max_length=1000)
    data_type = models.CharField(max_length=50, default="STRING", choices=WORKFLOW_INPUT_TYPES)
    default_value = models.JSONField() # type, value
    value = models.JSONField() # {type, value, options? }
    workflow = models.ForeignKey(to="Workflow", on_delete=models.CASCADE, related_name="input")


class WorflowComponent(models.Model):
    name = models.CharField(max_length=100)
    component = models.ForeignKey(to=ComponentDefinition, on_delete=models.CASCADE, related_name="instances")
    options = models.JSONField() # predefined
    # input: related
    # output: related
    version_number = models.IntegerField(default=1)
    
    def add_action_to_flow(self, action, previous_action=None):
        with transaction.atomic():
            new_step_action = WorkflowStepAction.objects.create(action=self)
            if previous_action:
                next_action = previous_action.next_action
                previous_action.next_action = new_step_action
                previous_action.save()
                if next_action:
                    new_step_action.next_action = next_action
                    new_step_action.save()


            
class WorkflowStepAction(models.Model):
    updated_at = models.DateTimeField(auto_now=True)
    action = models.ForeignKey(to=WorflowComponent, on_delete=models.CASCADE, related_name="steps")
    next_action = models.ForeignKey(to=WorflowComponent, on_delete=models.CASCADE, related_name="next_steps")
   

class Workflow(models.Model):
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=1000)
    current_active_version = models.CharField(max_length=15, default="0.0")
    workflow_file = models.FileField(max_length=1000, upload_to=upload_to_path)
    created_at = models.DateTimeField(auto_now_add=True)

    # if we make this DB only
    version_number = models.IntegerField(default=1)
    
    entrypoint = models.ForeignKey(WorflowComponent, on_delete=models.CASCADE, related_name="workflows")
    # input: related field


class WorkFlowInstance(models.Model):
    workflow = models.ForeignKey(to=Workflow, on_delete=models.CASCADE, related_name="instances")
    created_at = models.DateTimeField(auto_now_add=True)
    variables = models.JSONField()
    status = models.CharField(max_length=50, choices=WORKFLOW_STATUS, default='PENDING')

    # Current task
    # start task



class WorkflowActionInstance(models.Model):
    workflow = models.ForeignKey(WorkFlowInstance, on_delete=models.CASCADE, related_name="child_actions")
    action = models.ForeignKey(WorkflowStepAction, on_delete=models.CASCADE)
    parent_action = models.ForeignKey(WorkflowStepAction, on_delete=models.CASCADE, 
                                    null=True, blank=True, related_name="child_actions")
    output = models.JSONField()
    input = models.JSONField()

    status = models.CharField(max_length=50, choices=WORKFLOW_STATUS, default='PENDING')

