from django.db import models
import uuid

from django.conf import settings
from django.core.files.storage import FileSystemStorage


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

def get_unique_id():
    return str(uuid.uuid4())

def upload_to_path(instance, filename):
    return f"workflows/{instance.id}/{instance.current_active_version}"

# Create your models here.



class WorkflowAction(models.Model):
    name = models.CharField(max_length=100)
    is_function = models.BooleanField(default=True) # else it's a class. TBD
    path_to_execute = models.CharField(max_length=1000, null=True, blank=True) # class name or class path 
    code_to_execute = models.TextField(default='print("Workflow action")')
    options = models.JSONField() # predefined

    input = models.JSONField()  # TODO: Define the structure of these fields. {key, value, type, args}
    output = models.JSONField()
    
    sub_actions = models.ManyToManyField(to="WorkflowStepAction", related_name="parent_actions")

    version_number = models.IntegerField(default=1)
    on_success = models.ForeignKey(to="WorkflowAction", on_delete=models.CASCADE, related_name="success_callback") # select a predefined action or passed by parent.
    on_error = models.ForeignKey(to="WorkflowAction", on_delete=models.CASCADE, related_name="error_callback") # select a predefined action or passed by parent.

class WorkflowStepAction(models.Model):
    order = models.SmallIntegerField(default=0)
    action = models.ForeignKey(to=WorkflowAction, on_delete=models.CASCADE)
   

class Workflow(models.Model):
    name = models.CharField(max_length=100)
    current_active_version = models.CharField(max_length=15, default="0.0")
    workflow_file = models.FileField(max_length=1000, upload_to=upload_to_path)
    created_at = models.DateTimeField(auto_now_add=True)

    # if we make this DB only
    definition = models.ManyToManyField(WorkflowStepAction)
    main_action = models.ForeignKey(WorkflowStepAction, on_delete=models.CASCADE, related_name="workflows")
    version_number = models.IntegerField(default=1)
    env_variables = models.JSONField()



class WorkFlowInstance(models.Model):
    workflow = models.ForeignKey(to=Workflow, on_delete=models.CASCADE, related_name="instances")
    created_at = models.DateTimeField(auto_now_add=True)
    variables = models.JSONField()
    status = models.CharField(max_length=50, choices=WORKFLOW_STATUS, default='PENDING')

class WorkflowActionInstance(models.Model):
    workflow = models.ForeignKey(WorkFlowInstance, on_delete=models.CASCADE, related_name="child_actions")
    action = models.ForeignKey(WorkflowStepAction, on_delete=models.CASCADE)
    parent_action = models.ForeignKey(WorkflowStepAction, on_delete=models.CASCADE, null=True, blank=True, related_name="child_actions")
    output = models.JSONField()
    input = models.JSONField()

    status = models.CharField(max_length=50, choices=WORKFLOW_STATUS, default='PENDING')

