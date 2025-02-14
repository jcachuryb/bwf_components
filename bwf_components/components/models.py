from django.db import models

VARIABLE_TYPES = [
    ("STRING", "string"),
    ("NUMBER", "number"),
    ("ARRAY", "array"),
    ("OBJECT", "object"),
    ("BOOLEAN", "boolean"),
]

OUTPUT_TYPES = [
    ("STRING", "string"),
    ("NUMBER", "number"),
    ("ARRAY", "array"),
    ("OBJECT", "object"),
    ("BOOLEAN", "boolean"),
]


CONTEXT_TYPES = [
    ("GLOBAL", "Global"),
    ("LOCAL", "Local"),
    ("INPUT", "Input"),
    ("SECRET", "Secret"),
    ("OUTPUT", "Output"),
]

FAILURE_HANDLE_TYPES = [
    ("RETRY", "Retry"),
    ("IGNORE", "Ignore"),
    ("TERMINATE", "Terminate"),
    ("CUSTOM", "Custom"),
]



class WorkflowComponent(models.Model):
    name = models.CharField(max_length=100)
    component = models.ForeignKey(to="ComponentDefinition", on_delete=models.CASCADE, related_name="instances")
    options = models.JSONField() # predefined
    # input: related
    # output: related
    # action_flow: related
    version_number = models.IntegerField(default=1)

    def get_input_values(self, context_inputs={}):
        inputs = self.input.all().select_related("dependencies").defer("parent")
        values = {} 
        for input in inputs:
            values[input.key] = {"key": input.key, "value": input.get_value(context_inputs), "label": input.name}


class VariableValue(models.Model):
    label = models.CharField(max_length=100)
    key = models.CharField(max_length=100)
    data_type = models.CharField(max_length=50, default="STRING", choices=VARIABLE_TYPES)
    value = models.TextField()
    context_name = models.CharField(max_length=10, default="LOCAL", choices=CONTEXT_TYPES)


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
            return eval(self.expression, context_inputs)
        if self.json_value:
            expression = self.json_value.get("expression", None)
            value = self.json_value.get("value", None)
            if value:
                return value
            if expression:
                return eval(expression, context_inputs)
        return None
            


class ComponentOutput(models.Model):
    name = models.CharField(max_length=100)
    data_type = models.CharField(max_length=50, default="STRING", choices=OUTPUT_TYPES)
    value = models.TextField()
    component = models.ForeignKey(to=WorkflowComponent, on_delete=models.CASCADE, related_name="output")
    is_custom = models.BooleanField(default=False)


class ComponentDefinition(models.Model):
    name = models.CharField(max_length=100)
    path_to_execute = models.CharField(max_length=1000, null=True, blank=True) # class name or class path 
    script = models.TextField(default='print("Workflow action")')
    base_input = models.JSONField()  # TODO: Define the structure of these fields. {key, label, value, type, index}
    base_output = models.JSONField()
    version_number = models.IntegerField(default=1)
    version_name = models.CharField(max_length=15, default="0.0")
    editable = models.BooleanField(default=True)
    children_components = models.BooleanField(default=False)
    # input : One to Many


class OnComponentFail(models.Model):
    type = models.CharField(max_length=15, choices=FAILURE_HANDLE_TYPES, default="Retry")
    max_retries = models.SmallIntegerField(default=1, blank=True, null=True)
    retry_interval = models.IntegerField(blank=True, null=True)
    component = models.ForeignKey(to=WorkflowComponent, on_delete=models.CASCADE, blank=True, null=True)

