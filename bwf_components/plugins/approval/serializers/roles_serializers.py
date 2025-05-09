from ..models import BWF_Role
from rest_framework import serializers

class BWF_RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = BWF_Role
        fields = ['id', 'system_name', 'name', 'description']
        read_only_fields = ['id']