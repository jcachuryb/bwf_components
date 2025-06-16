from django.contrib import admin
from bwf_components.plugins.approval.models import ApprovalUser, BWF_Role, FormApproval

# Register your models here.

admin.site.register(ApprovalUser)
admin.site.register(BWF_Role)
admin.site.register(FormApproval)