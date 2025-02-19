import importlib

from django.db import models

class OutputTypesEnum(models.TextChoices):
    STRING = "STRING", "string"
    NUMBER = "NUMBER", "number"
    ARRAY = "ARRAY", "array"
    OBJECT = "OBJECT", "object"
    BOOLEAN = "BOOLEAN", "boolean"

class FailureHandleTypesEnum(models.TextChoices):
    RETRY = "RETRY", "Retry"
    IGNORE = "IGNORE", "Ignore"
    TERMINATE = "TERMINATE", "Terminate"
    CUSTOM = "CUSTOM", "Custom"


class WorkflowComponent(models.Model):
    name = models.CharField(max_length=100)
    definition = models.ForeignKey(to="ComponentDefinition", on_delete=models.CASCADE, related_name="instances")
    options = models.JSONField() # predefined
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

    def get_component_class(self):
        path_array = self.definition.path_to_execute.rsplit(".", 1)

        module = importlib.import_module(path_array[0])
        class_ = getattr(module, path_array[1])
        # instance = class_()
        return class_

    def __str__(self):
        return f"{self.name} - {self.definition.name} - {self.version_number}"


class ComponentInput(models.Model):
    name = models.CharField(max_length=100)
    key = models.CharField(max_length=100)
    expression = models.TextField(default='')
    json_value = models.JSONField() # {key, label, type, value}
    index = models.SmallIntegerField(default=0)
    parent = models.ForeignKey(to=WorkflowComponent, on_delete=models.CASCADE, related_name="input")
    required = models.BooleanField(default=False)
    is_custom = models.BooleanField(default=False) # In case you can add custom inputs to components

    def get_value(self, context_inputs={}):
        if self.expression:
            return eval(self.expression, None, {"context": context_inputs})
        if self.json_value:
            expression = self.json_value.get("expression", None)
            value = self.json_value.get("value", None)
            if value:
                return value
            if expression:
                return eval(expression, None, {"context": context_inputs})
        return None
            


class ComponentOutput(models.Model):
    name = models.CharField(max_length=100)
    data_type = models.CharField(max_length=50, default=OutputTypesEnum.STRING, choices=OutputTypesEnum.choices)
    value = models.TextField()
    component = models.ForeignKey(to=WorkflowComponent, on_delete=models.CASCADE, related_name="output")
    is_custom = models.BooleanField(default=False)


class ComponentDefinition(models.Model):
    name = models.CharField(max_length=100)
    path_to_execute = models.CharField(max_length=1000, null=True, blank=True) # class name or class path 
    script = models.TextField(default='print("Workflow action")')
    base_input = models.JSONField()  # TODO: Define the structure of these fields. {key, label, value, type, index}
    base_output = models.JSONField(null=True, blank=True)
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