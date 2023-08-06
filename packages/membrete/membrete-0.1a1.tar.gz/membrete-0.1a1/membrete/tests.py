from django.test import TestCase
from django.test import Client

client = Client()
class TestMembrete(TestCase):
	def test_sent_raises_Http404(self): 
		request = client.get('/sent', {})
		self.assertEqual(request.status_code, 404)
