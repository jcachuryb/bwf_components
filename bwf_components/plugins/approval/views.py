from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.views import View

from .models import BWF_Role, FormApproval
from bwf_components.plugins.approval.serializers import (
    bwf_forms_serializers,
    roles_serializers,
)
from bwf_forms.models import (
    BwfForm, BwfFormVersion
)


class ApprovalFormVisualizerView(View):
    template_name = "approvals/form_approval.html"

    def get(self, request, *args, **kwargs):
        form_approval_id = kwargs.get("form_approval_id")

        # TODO: Validate user in session has role.

        approval_obj = FormApproval.objects.get(approval_id=form_approval_id)

        form_definition = approval_obj.form_version.definition
        context = {
            "form_approval_id": form_approval_id,
            "workflow_instance_id": approval_obj.workflow_instance_id,
            "component_instance_id": approval_obj.component_instance_id,
            "status": approval_obj.status,
        }
        # Assuming you have a method to render the form visualizer
        return render(request, self.template_name, context)

@api_view(["GET"])
def form_definition(request, form_approval_id):
    """
    Retrieve the form definition for a given form approval ID.
    """
    try:
        approval_obj = FormApproval.objects.get(approval_id=form_approval_id)
        form_version = approval_obj.form_version
        serializer = bwf_forms_serializers.FormDefinitionSerializer(
            {"form_definition": form_version.get_json_form_structure()}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)
    except FormApproval.DoesNotExist:
        return Response(
            {"error": "Form approval not found."}, status=status.HTTP_404_NOT_FOUND
        )


class BWF_RoleListView(ListAPIView):
    def get(self, request, *args, **kwargs):
        queryset = BWF_Role.objects.all()
        serializer = roles_serializers.BaseListSerializer(queryset, many=True)
        return Response(serializer.data)


class BWF_ApprovalFormListView(ListAPIView):
    def get(self, request, *args, **kwargs):
        queryset = BwfForm.objects.filter(is_active=True, version_id__isnull=False)
        serializer = bwf_forms_serializers.BWFFormsSerializer(queryset, many=True)
        return Response(serializer.data)
