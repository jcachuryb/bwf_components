from ..models import BWF_Role
from rest_framework import serializers

class BaseListSerializer(serializers.Serializer):
    def to_representation(self, instance):
        return {
            'id': instance.id,
            'name': instance.name,
            'extra': {
                'system_name': instance.system_name,
                'description': instance.description
            }
        }


class BWF_RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = BWF_Role
        fields = ['id', 'system_name', 'name', 'description']
        read_only_fields = ['id']