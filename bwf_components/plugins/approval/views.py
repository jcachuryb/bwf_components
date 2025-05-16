from rest_framework.generics import ListAPIView
from rest_framework.response import Response

from .models import BWF_Role, ApprovalUser
from .serializers import roles_serializers



class BWF_RoleListView(ListAPIView):
    def get(self, request, *args, **kwargs):
        queryset = BWF_Role.objects.all()
        serializer = roles_serializers.BaseListSerializer(queryset, many=True)
        return Response(serializer.data)