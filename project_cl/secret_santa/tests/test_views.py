from django.urls import reverse
from django.http import HttpResponse
from django.test import TestCase
import pytest
from django.test import Client
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login


# main function: secret_santa



# tests for every view x2 -> 40

class MainViewTest(TestCase):
    def test_main_view_status_code(self):
        client = Client()
        response = client.get(reverse('index'))

        self.assertEqual(response.status_code, 200)

    def test_main_view_response_type(self):
        client = Client()
        response = client.get(reverse('index'))

        self.assertIsInstance(response, HttpResponse)

    def test_main_view_template_used(self):
        client = Client()
        response = client.get(reverse('index'))

        self.assertTemplateUsed(response, 'index.html')