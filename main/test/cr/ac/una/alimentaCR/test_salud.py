from django.test import TestCase
from django.urls import reverse


class VistaSaludTest(TestCase):

    def test_salud_retorna_up(self):
        response = self.client.get(reverse("salud"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            "status": "UP"
        })