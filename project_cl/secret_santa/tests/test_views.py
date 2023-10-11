from django.urls import reverse
from django.http import HttpResponse
from django.test import TestCase
import pytest
from django.test import Client
from django.contrib.auth.models import User
from secret_santa.models import Group, Event, Participant



### main views ###

class LoggedUserViewTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_logged_user_view_for_authenticated_user(self):
        user = User.objects.create(username='testuser')
        user.set_password('testpassword')
        user.save()
        self.client.login(username='testuser', password='testpassword')

        response = self.client.get(reverse('base'))

        self.assertEqual(response.status_code, 200)

    def test_logged_user_view_displays_user_info(self):
        user = User.objects.create(username='testuser')
        user.set_password('testpassword')
        user.save()
        self.client.login(username='testuser', password='testpassword')

        response = self.client.get(reverse('base'))

        self.assertEqual(response.status_code, 200)

        self.assertContains(response, 'User logged: testuser')

        self.assertContains(response, '<a class="menu-link" href="/logout/">Logout</a>')

    def test_logged_user_view_displays_games(self):
        user = User.objects.create(username='testuser')
        user.set_password('testpassword')
        user.save()
        self.client.login(username='testuser', password='testpassword')

        response = self.client.get(reverse('base'))

        self.assertContains(response, 'Games created by me')


class QuickGameViewTests(TestCase):
    def test_quick_game_view_form_displayed(self):
        response = self.client.get(reverse('quick_game'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Max price')
        self.assertContains(response, 'Currency')
        self.assertContains(response, 'Date')

    def test_quick_game_form_submission(self):
        data = {
            'max_price': 50.00,
            'currency': 'USD',
            'date': '2023-12-25',
            'num_players': 3,
            'player_name_1': 'Player 1',
            'player_email_1': 'player1@example.com',
            'player_name_2': 'Player 2',
            'player_email_2': 'player2@example.com',
            'player_name_3': 'Player 3',
            'player_email_3': 'player3@example.com',
        }
        response = self.client.post(reverse('quick_game'), data)
        self.assertEqual(response.status_code, 302)


class GameViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.login(username='testuser', password='testpassword')

    def test_game_view_form_displayed(self):
        response = self.client.get(reverse('new-game'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Event')
        self.assertContains(response, 'Group')
        self.assertContains(response, 'Date')

    def test_game_form_submission(self):
        event = Event.objects.create(name='Test Event', organizer=self.user)
        group = Group.objects.create(name='Test Group', creator=self.user, price_limit=50, currency='PLN')

        data = {
            'event': event.id,
            'group': group.id,
            'date': '2023-12-25',
        }
        response = self.client.post(reverse('new-game'), data)
        self.assertEqual(response.status_code, 302)


