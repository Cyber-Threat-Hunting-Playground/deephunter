from django.test import TestCase, Client
from django.urls import reverse
from .models import Analytic, Category
from connectors.models import Connector
from config.models import ApiKey

class AnalyticAPITestCase(TestCase):
    def setUp(self):
        self.client = Client()
        connector = Connector.objects.create(name='Test Connector', connector_type='TEST')
        category = Category.objects.create(name='Test Category', short_name='TC', description='Test')
        
        self.analytic1 = Analytic.objects.create(
            name='Test Analytic 1',
            query='SELECT * FROM test',
            status='PUB',
            connector=connector,
            category=category
        )
        self.analytic2 = Analytic.objects.create(
            name='Test Analytic 2',
            query='SELECT * FROM test2',
            status='DRAFT',
            connector=connector,
            category=category
        )
        self.api_key = ApiKey.objects.create(name='Test Key', key='testkey123', key_type='READ')

    def test_get_analytics(self):
        response = self.client.get(reverse('analytic-list'), HTTP_AUTHORIZATION=f'Bearer {self.api_key.key}')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('results', data)
        self.assertEqual(len(data['results']), 2)

    def test_get_analytics_with_status_filter(self):
        response = self.client.get(reverse('analytic-list'), {'status': 'PUB'}, HTTP_AUTHORIZATION=f'Bearer {self.api_key.key}')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data['results']), 1)
        self.assertEqual(data['results'][0]['name'], 'Test Analytic 1')

    def test_get_analytic_detail(self):
        response = self.client.get(reverse('analytic-detail', args=[self.analytic1.pk]), HTTP_AUTHORIZATION=f'Bearer {self.api_key.key}')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['name'], 'Test Analytic 1')

    def test_get_analytic_detail_not_found(self):
        response = self.client.get(reverse('analytic-detail', args=[999]), HTTP_AUTHORIZATION=f'Bearer {self.api_key.key}')
        self.assertEqual(response.status_code, 404)

    def test_unauthorized_access(self):
        response = self.client.get(reverse('analytic-detail', args=[self.analytic1.pk]))
        self.assertEqual(response.status_code, 403)
