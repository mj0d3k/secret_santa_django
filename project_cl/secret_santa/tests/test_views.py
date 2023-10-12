import random
from django.urls import reverse
from django.http import HttpResponse
from django.test import TestCase
import pytest
from django.test import Client
from django.contrib.auth.models import User
from secret_santa.models import Group, Event, Participant
from django.contrib.auth import authenticate, login, logout
from secret_santa.forms import EventForm, GroupForm, ParticipantForm
from secret_santa.views import secret_santa
from django.core import mail


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


class LookupViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.login(username='testuser', password='testpassword')

    def test_lookup_view_displayed(self):
        response = self.client.get(reverse('email-lookup'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Email Lookup')
        self.assertContains(response, 'Enter your email')

    def test_lookup_invalid_email(self):
        response = self.client.post(reverse('email-lookup'), {'email': 'invalid-email'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Enter a valid email address.')


class MyGiftPairsViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.login(username='testuser', password='testpassword')

    def test_my_gift_pairs_no_pairs(self):
        response = self.client.get(reverse('my-gift-pairs'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Your email does not participate in any games yet.')

    def test_my_gift_pairs_with_pairs(self):

        response = self.client.get(reverse('my-gift-pairs'))
        self.assertEqual(response.status_code, 200)


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


class LoginViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.login_url = reverse('login')
        self.user = User.objects.create_user(username='testuser', password='testpassword')

    def test_get_login_page(self):
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login_user_view.html')

    def test_post_login_valid_credentials(self):
        response = self.client.post(self.login_url, {'username': 'testuser', 'password': 'testpassword'})
        self.assertRedirects(response, reverse('base'), fetch_redirect_response=False)
    

class LogoutViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.logout_url = reverse('logout')
        self.user = User.objects.create_user(username='testuser', password='testpassword')

    def test_logout_authenticated_user(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(self.logout_url)

        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_logout_redirect_for_authenticated_user(self):
        # Log in the user
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('login'))

        self.assertRedirects(response, reverse('base'))


class ChangePasswordViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.change_password_url = reverse('change-password')

    def test_change_password_redirects_to_login(self):
        self.client.login(username='testuser', password='testpassword')

        self.client.post(self.change_password_url, {
            'old_password': 'testpassword',
            'new_password1': 'newpassword123',
            'new_password2': 'newpassword123',
        })


class DeleteAccountViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.delete_account_url = reverse('delete_account', args=[self.user.id])

    def test_delete_account_redirects_to_index(self):
        self.client.login(username='testuser', password='testpassword')

        response = self.client.post(self.delete_account_url)

        self.assertEqual(response.status_code, 302)

        self.assertRedirects(response, reverse('index'))

    def test_user_can_delete_account(self):
        self.client.login(username='testuser', password='testpassword')

        response = self.client.get(self.delete_account_url)

        self.assertEqual(response.status_code, 200)

        self.assertTemplateUsed(response, 'user_delete_confirm.html')


