import uuid
import json
import collections.abc

from django.db import models
from django.conf import settings
from django.core.files.storage import FileSystemStorage

from bwf_components.components.models import WorkflowComponent


upload_storage = FileSystemStorage(location=settings.PRIVATE_MEDIA_ROOT)

class WorkflowStatusEnum(models.TextChoices):
    PENDING = "PENDING", "initial"
    RUNNING = "RUNNING", "running"
    COMPLETED = "COMPLETED", "completed"
    ERROR = "ERROR",  "error"


class ComponentStepStatusEnum(models.TextChoices):
    PENDING = "PENDING", "initial"
    RUNNING = "RUNNING", "running"
    COMPLETED = "COMPLETED", "completed"
    ERROR = "ERROR", "error"

class WorkflowInputTypesEnum(models.TextChoices):
    STRING = "STRING", "string"
    NUMBER = "NUMBER", "number"
    ARRAY = "ARRAY", "array"
    OBJECT = "OBJECT", "object"
    BOOLEAN = "BOOLEAN", "boolean"
    SELECT = "SELECT", "select"
    MULTI_SELECT = "MULTI_SELECT", "multi_select"
    FILE = "FILE", "file"
    ANY = "ANY", "any"

class VariableTypesEnum(models.TextChoices):
    STRING = "STRING", "string"
    NUMBER = "NUMBER", "number"
    ARRAY = "ARRAY", "array"
    OBJECT = "OBJECT", "object"
    BOOLEAN = "BOOLEAN", "boolean"

class ContextTypesEnum(models.TextChoices):
    GLOBAL = "GLOBAL", "Global"
    LOCAL = "LOCAL", "Local"
    INPUT = "INPUT", "Input"
    SECRET = "SECRET", "Secret"


def get_unique_id():
    return str(uuid.uuid4())

def upload_to_path(instance, filename):
    return f"workflows/{instance.id}/{instance.current_active_version}"

# TODO: Context Class


class VariableValue(models.Model):
    label = models.CharField(max_length=100)
    key = models.CharField(max_length=100)
    data_type = models.CharField(max_length=50, default=VariableTypesEnum.STRING, choices=VariableTypesEnum.choices)
    value = models.TextField()
    context_name = models.CharField(max_length=10, default=ContextTypesEnum.LOCAL, choices=ContextTypesEnum.choices)
    workflow = models.ForeignKey(to="Workflow", on_delete=models.CASCADE, related_name="variables")


class WorkflowInput(models.Model):
    label = models.CharField(max_length=100)
    key = models.CharField(max_length=100)
    description = models.CharField(max_length=1000)
    data_type = models.CharField(max_length=50, default=WorkflowInputTypesEnum.STRING, choices=WorkflowInputTypesEnum.choices)
    default_value = models.JSONField() # type, value
    value = models.JSONField() # {type, value, options? }
    workflow = models.ForeignKey(to="Workflow", on_delete=models.CASCADE, related_name="input")


    
class WorkflowCluster(models.Model):
    label = models.CharField(default="Component Flow")
    parent_component = models.ForeignKey(WorkflowComponent, on_delete=models.CASCADE, 
                               related_name="action_flow", null=True, blank=True)
    components = models.ManyToManyField(WorkflowComponent, through="ClusterComponent", related_name="clusters")
    is_sequential = models.BooleanField(default=True)
    is_exclusive = models.BooleanField(default=False)
    is_fixed = models.BooleanField(default=False)
    # components: related


class ClusterComponent(models.Model):
    updated_at = models.DateTimeField(auto_now=True)
    index = models.SmallIntegerField(default=0)
    component = models.ForeignKey(to=WorkflowComponent, on_delete=models.CASCADE, related_name="step")
    cluster = models.ForeignKey(WorkflowCluster, on_delete=models.CASCADE, related_name="child_components")


class Workflow(models.Model):
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=1000, null=True, blank=True)
    current_active_version = models.CharField(max_length=15, default="0.0")
    workflow_file = models.FileField(max_length=1000, upload_to=upload_to_path, null=True, blank=True, storage=upload_storage)
    created_at = models.DateTimeField(auto_now_add=True)

    # if we make this DB only
    version_number = models.IntegerField(default=1)
    cluster = models.ForeignKey(WorkflowCluster, on_delete=models.CASCADE, related_name="workflows")
    # entrypoint = models.ForeignKey(WorkflowComponent, on_delete=models.CASCADE, related_name="workflows")

    # input: related field


class WorkFlowInstance(models.Model):
    workflow = models.ForeignKey(to=Workflow, on_delete=models.CASCADE, related_name="instances")
    created_at = models.DateTimeField(auto_now_add=True)
    variables = models.JSONField()
    status = models.CharField(max_length=50, choices=ComponentStepStatusEnum.choices, default=ComponentStepStatusEnum.PENDING)
    # Current task
    # start task



class ComponentInstance(models.Model):
    workflow = models.ForeignKey(WorkFlowInstance, on_delete=models.CASCADE, related_name="child_actions")
    component = models.ForeignKey(WorkflowComponent, on_delete=models.CASCADE)
    parent_action = models.ForeignKey(WorkflowComponent, on_delete=models.CASCADE, 
                                    null=True, blank=True, related_name="child_actions")
    output = models.JSONField()
    input = models.JSONField()

    status = models.CharField(max_length=50, choices=WorkflowStatusEnum.choices, default=WorkflowStatusEnum.PENDING)


class WorkflowInstanceFactory:

    @staticmethod
    def create_workflow(workflow, input_params={}):

        instance = WorkFlowInstance.objects.create(workflow=workflow)
        # collect variables
        input_values = workflow.input.all()
        context = {}
        for input in input_values:
            context['input'][input.key] = WorkflowInstanceFactory.__get_input_value(input, input_params.get(input.key))
        instance.variables = json.dump(context)
        instance.save()
        return instance

    @staticmethod
    def __get_input_value(input_value: WorkflowInput, param_value=None):
        input_type = input_value.data_type
        json_default = json.load(input_value.default_value)
        json_value = json.load(input_value.default_value)

        if param_value is None:
            return json_default['value']
        else:
            if input_type in [WorkflowInputTypesEnum.SELECT, WorkflowInputTypesEnum.MULTI_SELECT]:
                values = []
                param_value = param_value if isinstance(param_value, collections.abc.Sequence) else [param_value]
                options = json_value.value['options']
                for option in options:
                    if option['key'] in param_value:
                        values.append(option['key'])
                
                return values
            else:
                if input_type == WorkflowInputTypesEnum.NUMBER:
                    return int(param_value)
                elif input_type == WorkflowInputTypesEnum.BOOLEAN:
                    return bool(param_value)
                else:
                    return param_value

        