from django.test import TestCase, Client
from django.urls import reverse
from .models import Connector
from config.models import ApiKey

class ConnectorAPITestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.connector1 = Connector.objects.create(
            name='Test Connector 1',
            domain='analytics'
        )
        self.api_key = ApiKey.objects.create(name='Test Key', key='testkey123', key_type='READ')

    def test_get_connectors(self):
        response = self.client.get(reverse('connector-list'), HTTP_AUTHORIZATION=f'Bearer {self.api_key.key}')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data['results']), 1)

    def test_get_connector_detail(self):
        response = self.client.get(reverse('connector-detail', args=[self.connector1.pk]), HTTP_AUTHORIZATION=f'Bearer {self.api_key.key}')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['name'], 'Test Connector 1')
