import uuid
from django.db import models
from django.db.models.functions import Lower
from bwf_components.bwf_forms.models import (
    BwfFormVersion,
)

# Create your models here.


class ApprovalUser(models.Model):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = "User"
        constraints = [
            models.UniqueConstraint(Lower("email"), name="approvals_unique_email"),
        ]


class BWF_Role(models.Model):
    system_name = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "BWF Role"
        constraints = [
            models.UniqueConstraint(
                fields=["system_name", "name"], name="approvals_unique_name_system"
            ),
        ]


class FormApproval(models.Model):
    approval_id = models.CharField(max_length=100, unique=True)
    form_version = models.ForeignKey(BwfFormVersion, on_delete=models.CASCADE)
    workflow_instance_id = models.IntegerField()
    component_instance_id = models.IntegerField()

    # Roles associated with this approval form (?)
    # approved_by_email

    def __str__(self):
        return f"{self.form_version.form.name}"

    def save(self, *args, **kwargs):
        if not self.pk:
            # Generate a unique approval ID if not already set
            if not self.approval_id:
                self.approval_id = f"{str(uuid.uuid4())}-{self.form_version.id}-{self.workflow_instance_id}-{self.component_instance_id}"
        return super().save(*args, **kwargs)


class ApprovalRecord(models.Model):
    user = models.ForeignKey(ApprovalUser, on_delete=models.CASCADE)
    role = models.ForeignKey(BWF_Role, on_delete=models.CASCADE)
    approved = models.BooleanField(default=False)
    date_approved = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user} - {self.role} - {self.approved}"
