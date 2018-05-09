from datahub.investment.models import (
    InvestmentProject as DBInvestmentProject,
    InvestmentProjectPermission,
)
from datahub.investment.permissions import (
    get_association_filters, InvestmentProjectAssociationChecker
)
from .models import InvestmentProject
from .views import SearchInvestmentProjectAPIView, SearchInvestmentProjectExportAPIView
from ..apps import EXCLUDE_ALL, SearchApp


class InvestmentSearchApp(SearchApp):
    """SearchApp for investment"""

    name = 'investment_project'
    es_model = InvestmentProject
    # Investment project documents are very large, so the bulk_batch_size is set to a lower value
    # to keep bulk requests below 10 MB.
    # (In some environments, the maximum ES request size is 10 MB. This is dependent on the AWS
    # EC2 instance type.)
    bulk_batch_size = 1000
    view = SearchInvestmentProjectAPIView
    export_view = SearchInvestmentProjectExportAPIView
    permission_required = (
        f'investment.{InvestmentProjectPermission.read_all}',
        f'investment.{InvestmentProjectPermission.read_associated}'
    )
    queryset = DBInvestmentProject.objects.select_related(
        'archived_by',
        'average_salary',
        'client_relationship_manager',
        'fdi_type',
        'intermediate_company',
        'investment_type',
        'investmentprojectcode',
        'investor_company',
        'investor_type',
        'level_of_involvement',
        'project_assurance_adviser',
        'project_manager',
        'referral_source_activity',
        'referral_source_activity_marketing',
        'referral_source_activity_website',
        'referral_source_adviser',
        'sector',
        'sector__parent',
        'sector__parent__parent',
        'specific_programme',
        'stage',
        'uk_company',
    )

    def get_permission_filters(self, request):
        """
        Gets permission filter arguments.

        If a user only has permission to access projects associated to their team, this returns
        the filters that should be applied to only return those projects.
        """
        checker = InvestmentProjectAssociationChecker()

        if not checker.should_apply_restrictions(request, 'list'):
            return None

        if checker.should_exclude_all(request):
            return EXCLUDE_ALL

        dit_team_id = request.user.dit_team_id
        to_one_filters, to_many_filters = get_association_filters(dit_team_id)

        filters = {f'{field}.dit_team.id': value for field, value in to_one_filters}
        filters.update({
            f'{field.es_field_name}.dit_team.id': value for field, value in to_many_filters
        })

        return filters
