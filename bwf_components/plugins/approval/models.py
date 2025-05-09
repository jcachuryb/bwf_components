from django.db import models
from django.db.models.functions import Lower

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
            models.UniqueConstraint(Lower('email'), name='unique_email'),
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
            models.UniqueConstraint(fields=["system_name", "name"], name="approval_unique_name_system"),
        ]


class Approval(models.Model):
    user = models.ForeignKey(ApprovalUser, on_delete=models.CASCADE)
    role = models.ForeignKey(BWF_Role, on_delete=models.CASCADE)
    approved = models.BooleanField(default=False)
    date_approved = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user} - {self.role} - {self.approved}"