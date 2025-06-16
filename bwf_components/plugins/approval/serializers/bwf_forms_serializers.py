from bwf_components.bwf_forms.models import (
    BwfForm,
    BwfFormVersion,
)
from rest_framework import serializers


class BWFFormsSerializer(serializers.ModelSerializer):
    class Meta:
        model = BwfForm
        fields = "__all__"


class BWFFormsVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = BwfFormVersion
        fields = "__all__"


class FormDefinitionSerializer(serializers.Serializer):
    form_definition = serializers.JSONField()
