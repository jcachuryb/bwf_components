import importlib

from django.db import models

class InputOutputTypesEnum(models.TextChoices):
    STRING = "string", "string"
    NUMBER = "number", "number"
    ARRAY = "array", "array"
    OBJECT = "object", "object"
    BOOLEAN = "boolean", "boolean"

class FailureHandleTypesEnum(models.TextChoices):
    RETRY = "RETRY", "Retry"
    IGNORE = "IGNORE", "Ignore"
    TERMINATE = "TERMINATE", "Terminate"
    CUSTOM = "CUSTOM", "Custom"


class WorkflowComponent(models.Model):
    name = models.CharField(max_length=100)
    plugin_id = models.CharField(max_length=500, null=True, blank=True)    

    options = models.JSONField(null=True, blank=True) # predefined
    # input: related
    # output: related
    # action_flow: related
    parent_workflow = models.ForeignKey(to="workflow.Workflow", on_delete=models.CASCADE, related_name="components")
    version_number = models.IntegerField(default=1)

    def get_input_values(self, context_inputs={}):
        inputs = self.input.all()
        values = {} 
        for input in inputs:
            values[input.key] = {"key": input.key, "value": input.get_value(context_inputs), "label": input.name}
        return values

    def __str__(self):
        return f"{self.name} - {self.plugin_id} - {self.version_number}"


class ComponentDefinition(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=1000, default="")
    path_to_execute = models.CharField(max_length=1000, null=True, blank=True) # class name or class path 
    script = models.TextField(default='print("Workflow action")')
    base_input = models.JSONField()  # {key, label, value, type, index} value:  expression, variable, value
    base_output = models.JSONField(null=True, blank=True) # {key, label, value, type, index}
    version_number = models.IntegerField(default=1)
    version_name = models.CharField(max_length=15, default="0.0")
    editable = models.BooleanField(default=True)
    children_components = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.name} - {self.path_to_execute}"


class OnComponentFail(models.Model):
    type = models.CharField(max_length=15, choices=FailureHandleTypesEnum.choices , default=FailureHandleTypesEnum.RETRY)
    max_retries = models.SmallIntegerField(default=1, blank=True, null=True)
    retry_interval = models.IntegerField(blank=True, null=True)
    num_retries = models.SmallIntegerField(default=0)
    component = models.ForeignKey(to=WorkflowComponent, on_delete=models.CASCADE, blank=True, null=True, related_name="on_fail")
    # alternative_flow = models.ForeignKey(to="workflow.WorkflowInstance", on_delete=models.CASCADE, blank=True, null=True, related_name="on_fail")

    def get_retry_interval_in_seconds(self):
        return self.retry_interval if self.retry_interval else 5