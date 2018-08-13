from django.conf import settings
from django.http import Http404
from django_filters.rest_framework import DjangoFilterBackend
from oauth2_provider.contrib.rest_framework.permissions import IsAuthenticatedOrTokenHasScope
from rest_framework import status
from rest_framework.filters import OrderingFilter
from rest_framework.response import Response

from datahub.core.viewsets import CoreViewSet
from datahub.investment.evidence.models import EvidenceGroup
from datahub.investment.evidence.permissions import (
    EvidenceGroupModelPermissions,
    IsAssociatedToInvestmentProjectEvidenceGroupFilter,
    IsAssociatedToInvestmentProjectEvidenceGroupPermission,
)
from datahub.investment.evidence.serializers import (
    CreateEvidenceGroupSerializer, EvidenceGroupSerializer
)
from datahub.investment.models import InvestmentProject
from datahub.oauth.scopes import Scope

MAX_LENGTH = settings.CHAR_FIELD_MAX_LENGTH


class EvidenceGroupViewSet(CoreViewSet):
    """ViewSet for public facing evidence group endpoint."""

    non_existent_project_error_message = 'Specified investment project does not exist'

    required_scopes = (Scope.internal_front_end,)
    permission_classes = (
        IsAuthenticatedOrTokenHasScope,
        EvidenceGroupModelPermissions,
        IsAssociatedToInvestmentProjectEvidenceGroupPermission,
    )
    serializer_class = EvidenceGroupSerializer
    queryset = EvidenceGroup.objects.select_related(
        'investment_project',
        'created_by',
        'modified_by',
    )
    filter_backends = (
        DjangoFilterBackend,
        IsAssociatedToInvestmentProjectEvidenceGroupFilter,
        OrderingFilter,
    )

    lookup_url_kwarg = 'evidence_group_pk'

    ordering_fields = ('created_on', 'name',)
    ordering = ('-created_on', 'name',)

    def get_queryset(self):
        """Filters the query set to the specified project."""
        self._check_project_exists()

        return self.queryset.filter(
            investment_project_id=self.kwargs['project_pk']
        )

    def create(self, request, *args, **kwargs):
        """Creates evidence group."""
        self._check_project_exists()

        serializer = CreateEvidenceGroupSerializer(
            data=request.data,
            context=self.get_serializer_context(),
        )
        serializer.is_valid(raise_exception=True)
        instance = serializer.save(**self.get_additional_data(True))
        return Response(
            self.get_serializer(instance=instance).data,
            status=status.HTTP_201_CREATED
        )

    def get_serializer_context(self):
        """Extra context provided to the serializer class."""
        context = {
            **super().get_serializer_context(),
            'current_user': self.request.user,
        }
        return context

    def get_additional_data(self, create):
        """Set investment project id from url parameter."""
        data = super().get_additional_data(create)
        if create:
            data['investment_project_id'] = self.kwargs['project_pk']
        return data

    def _check_project_exists(self):
        if not InvestmentProject.objects.filter(pk=self.kwargs['project_pk']).exists():
            raise Http404(self.non_existent_project_error_message)
