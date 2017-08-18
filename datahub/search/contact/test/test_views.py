import pytest
from rest_framework import status
from rest_framework.reverse import reverse

from datahub.company.test.factories import ContactFactory
from datahub.core.constants import Sector
from datahub.core.test_utils import APITestMixin

pytestmark = pytest.mark.django_db


@pytest.fixture
def setup_data():
    """Sets up data for the tests."""
    ContactFactory(first_name='abc', last_name='defg')
    ContactFactory(first_name='first', last_name='last')


class TestSearch(APITestMixin):
    """Tests search views."""

    def test_search_contact(self, setup_es, setup_data):
        """Tests detailed contact search."""
        setup_es.indices.refresh()

        term = 'abc defg'

        url = reverse('api-v3:search:contact')

        response = self.api_client.post(url, {
            'original_query': term,
            'last_name': 'defg',
        })

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['last_name'] == 'defg'

    def test_search_contact_no_filters(self, setup_es, setup_data):
        """Tests case where there is no filters provided."""
        setup_es.indices.refresh()

        url = reverse('api-v3:search:contact')
        response = self.api_client.post(url, {})

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) > 0

    def test_search_contact_sort_by_last_name_desc(self, setup_es, setup_data):
        """Tests sorting in descending order."""
        ContactFactory(first_name='test_name', last_name='abcdef')
        ContactFactory(first_name='test_name', last_name='bcdefg')
        ContactFactory(first_name='test_name', last_name='cdefgh')
        ContactFactory(first_name='test_name', last_name='defghi')

        setup_es.indices.refresh()

        term = 'test_name'

        url = reverse('api-v3:search:contact')
        response = self.api_client.post(url, {
            'original_query': term,
            'sortby': 'last_name:desc',
        })

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 4
        assert ['defghi',
                'cdefgh',
                'bcdefg',
                'abcdef'] == [contact['last_name'] for contact in response.data['results']]


class TestBasicSearch(APITestMixin):
    """Tests basic search view."""

    def test_basic_search_contacts(self, setup_es, setup_data):
        """Tests basic aggregate contacts query."""
        setup_es.indices.refresh()

        term = 'abc defg'

        url = reverse('api-v3:search:basic')
        response = self.api_client.get(url, {
            'term': term,
            'entity': 'contact'
        })

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1
        assert response.data['contacts'][0]['first_name'] in term
        assert response.data['contacts'][0]['last_name'] in term
        assert [{'count': 1, 'entity': 'contact'}] == response.data['aggregations']

    def test_search_contact_has_sector(self, setup_es, setup_data):
        """Tests sorting in descending order."""
        ContactFactory(first_name='sector_testing')

        setup_es.indices.refresh()

        term = 'sector_testing'

        url = reverse('api-v3:search:contact')
        response = self.api_client.post(url, {
            'original_query': term,
        })

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1

        sector_name = Sector.aerospace_assembly_aircraft.value.name
        assert sector_name == response.data['results'][0]['company_sector']['name']
