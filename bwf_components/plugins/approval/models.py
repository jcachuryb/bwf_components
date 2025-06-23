import uuid
from django.db import models
from django.db.models.functions import Lower
from bwf_forms.models import (
    BwfFormVersion,
)

# Create your models here.
class ApprovalActionTypesEnum(models.TextChoices):
    APPROVE = "approve", "Approve"
    REJECT = "reject", "Reject"

class ApprovalStatusEnum(models.TextChoices):
    PENDING = "pending", "Pending"
    APPROVED = "approved", "Approved"
    REJECTED = "rejected", "Rejected"
    CANCELLED = "cancelled", "Cancelled"

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
    status = models.CharField(
        max_length=20,
        choices=ApprovalStatusEnum.choices,
        default=ApprovalStatusEnum.PENDING,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    decision_due_date = models.DateTimeField(null=True, blank=True)

    # Roles associated with this approval form (?)
    # approved_by_email

    def __str__(self):
        return f"{self.form_version.form.name}"
    
    def approve(self):
        """
        Mark the approval as approved.
        """
        self.status = ApprovalStatusEnum.APPROVED
        self.save()
    
    def reject(self):
        """
        Mark the approval as rejected.
        """
        self.status = ApprovalStatusEnum.REJECTED
        self.save()
    
    def cancel(self):
        """
        Mark the approval as cancelled.
        """
        self.status = ApprovalStatusEnum.CANCELLED
        self.save()

    def save(self, *args, **kwargs):
        if not self.pk:
            # Generate a unique approval ID if not already set
            if not self.approval_id:
                self.approval_id = f"{str(uuid.uuid4())}-{self.form_version.id}-{self.workflow_instance_id}-{self.component_instance_id}"
        return super().save(*args, **kwargs)
    


class ApprovalRecord(models.Model):
    approval = models.ForeignKey(FormApproval, on_delete=models.CASCADE)
    user = models.ForeignKey(ApprovalUser, on_delete=models.CASCADE)
    role = models.ForeignKey(BWF_Role, on_delete=models.CASCADE)
    action = models.CharField(
        max_length=20,
        choices=ApprovalActionTypesEnum.choices,
        default=ApprovalActionTypesEnum.APPROVE,
    )
    approved = models.BooleanField(default=False)
    date_approved = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user} - {self.role} - {self.approved}"

def approval_record_factory(approval, user, role, action):
    """
    Factory function to create an ApprovalRecord instance.
    """
    return ApprovalRecord.objects.create(
        approval=approval,
        user=user,
        role=role,
        action=action,
        approved=(action == ApprovalActionTypesEnum.APPROVE),
    )