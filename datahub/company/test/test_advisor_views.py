from rest_framework import status
from rest_framework.reverse import reverse

from datahub.core.test_utils import APITestMixin
from .factories import AdviserFactory


class TestAdviser(APITestMixin):
    """Adviser test case."""

    def test_adviser_list_view(self):
        """Should return id and name."""
        AdviserFactory()
        url = reverse('api-v1:advisor-list')
        response = self.api_client.get(url)
        assert response.status_code == status.HTTP_200_OK

    def test_adviser_filtered_view(self):
        """Test filtering."""
        AdviserFactory(last_name='UNIQUE')
        url = reverse('api-v1:advisor-list')
        response = self.api_client.get(url, data=dict(last_name__icontains='uniq'))
        assert response.status_code == status.HTTP_200_OK
        result = response.json()
        assert len(result['results']) == 1
        assert result['results'][0]['last_name'] == 'UNIQUE'

    def test_adviser_list_view_default_sort_order(self):
        """Test default sorting."""
        AdviserFactory(first_name='a', last_name='sorted adviser')
        AdviserFactory(first_name='z', last_name='sorted adviser')
        AdviserFactory(first_name='f', last_name='sorted adviser')
        url = reverse('api-v1:advisor-list')
        response = self.api_client.get(url, data={
            'last_name__icontains': 'sorted'
        })
        assert response.status_code == status.HTTP_200_OK
        result = response.json()
        assert len(result['results']) == 3
        results = result['results']
        assert [res['name'] for res in results] == [
            'a sorted adviser',
            'f sorted adviser',
            'z sorted adviser',
        ]
