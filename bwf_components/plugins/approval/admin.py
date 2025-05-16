from django.contrib import admin
from bwf_components.plugins.approval.models import ApprovalUser, BWF_Role

# Register your models here.

admin.site.register(ApprovalUser)
admin.site.register(BWF_Role)
 