from django.db import models, transaction

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
    version_number = models.IntegerField(default=1)
    
    def add_action_to_flow(self, action, previous_action=None):
        from bwf_components.workflow.models import WorkflowStepAction
        with transaction.atomic():
            new_step_action = WorkflowStepAction.objects.create(action=self)
            if previous_action:
                next_action = previous_action.next_action
                previous_action.next_action = new_step_action
                previous_action.save()
                if next_action:
                    new_step_action.next_action = next_action
                    new_step_action.save()



class VariableValue(models.Model):
    label = models.CharField(max_length=100)
    key = models.CharField(max_length=100)
    data_type = models.CharField(max_length=50, default="STRING", choices=VARIABLE_TYPES)
    value = models.TextField()
    context_name = models.CharField(max_length=10, default="LOCAL", choices=CONTEXT_TYPES)


class ComponentInput(models.Model):
    name = models.CharField(max_length=100)
    expression = models.TextField(default='')
    json_value = models.JSONField() # {key, label, type, value}
    dependencies = models.ManyToManyField(VariableValue)
    parent = models.ForeignKey(to=WorkflowComponent, on_delete=models.CASCADE, related_name="input")
    required = models.BooleanField(default=False)
    is_custom = models.BooleanField(default=False)


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
    # input : One to Many


class OnComponentFail(models.Model):
    type = models.CharField(max_length=15, choices=FAILURE_HANDLE_TYPES, default="Retry")
    max_retries = models.SmallIntegerField(default=1, blank=True, null=True)
    retry_interval = models.IntegerField(blank=True, null=True)
    component = models.ForeignKey(to=WorkflowComponent, on_delete=models.CASCADE, blank=True, null=True)

