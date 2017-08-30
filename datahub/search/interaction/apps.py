from datahub.interaction.models import Interaction as DBInteraction
from datahub.search.apps import SearchApp
from datahub.search.interaction.models import Interaction
from datahub.search.interaction.views import SearchInteractionAPIView


class InteractionSearchApp(SearchApp):
    """SearchApp for interactions."""

    name = 'interaction'
    plural_name = 'interactions'
    ESModel = Interaction
    view = SearchInteractionAPIView
    queryset = DBInteraction.objects.prefetch_related(
        'company',
        'contact',
        'dit_adviser',
        'dit_team',
        'interaction_type',
        'investment_project',
        'service',
    )
