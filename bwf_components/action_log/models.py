from django.db import models
from bwf_components.workflow.models import WorkFlowInstance, ComponentInstance


class ActionLogStatusEnum(models.TextChoices):
    SUCCESS = "SUCCESS", "success"
    ERROR = "ERROR", "error"
    PENDING = "PENDING", "pending"
    STARTED = "STARTED", "started"
    STOPPED = "STOPPED", "stopped"
    RESTARTED = "RESTARTED", "restarted"
    TERMINATED = "TERMINATED", "terminated"
    

class ActionLog(models.Model):
    workflow_instance = models.ForeignKey(to=WorkFlowInstance, on_delete=models.SET_NULL, related_name="action_logs", null=True, blank=True)
    component_instance = models.ForeignKey(to=ComponentInstance, on_delete=models.SET_NULL, related_name="action_logs", null=True, blank=True)
    status = models.CharField(max_length=100, choices=ActionLogStatusEnum.choices, default=ActionLogStatusEnum.STARTED)
    error_message = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def job_id(self):
        return self.component_instance.id