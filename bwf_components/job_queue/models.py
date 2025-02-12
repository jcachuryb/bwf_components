from django.db import models

# Create your models here.
from workflow.models import WorkflowActionInstance, WorkFlowInstance

JOB_QUEUE_STATUS = (
    ("QUEUED", "QUEUED"),
    ("RUNNING", "RUNNING"),
    ("CANCELLED", "CANCELLED"),
    ("COMPLETED", "COMPLETED"),
    ("ERROR", "ERROR"),
)


class JobQueueRecord(models.Model):
    workflow = models.ForeignKey(WorkFlowInstance, on_delete=models.CASCADE, related_name="workflow_jobs")
    action = models.ForeignKey(WorkflowActionInstance, on_delete=models.CASCADE, related_name="action_job")
    created_at = models.DateTimeField(auto_now_add=True)
    message = models.CharField(max_length=1000, blank=True, null=True)
    status = models.CharField(choices=JOB_QUEUE_STATUS, default='QUEUED')


class JobQueueRecord(models.Model):
    action = models.ForeignKey(WorkflowActionInstance, on_delete=models.CASCADE, related_name="jobs")
    created_at = models.DateTimeField(auto_now_add=True)
    message = models.CharField(max_length=1000, blank=True, null=True)
    status = models.CharField(choices=JOB_QUEUE_STATUS, default='QUEUED')



