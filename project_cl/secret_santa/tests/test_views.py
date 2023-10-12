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


## EVENT SECTION ###

class EventTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpassword')

    def test_add_event_view_for_authenticated_user(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('add-event'))
        self.assertEqual(response.status_code, 200)

    def test_add_event_view_form_submission(self):
        self.client.login(username='testuser', password='testpassword')
        data = {
            'name': 'Test Event',
            'description': 'This is a test event',
            'organizer': self.user.id
        }
        response = self.client.post(reverse('add-event'), data)
        self.assertEqual(response.status_code, 302)

    def test_edit_event_view_for_authenticated_user(self):
        event = Event.objects.create(name='Test Event', description='This is a test event', organizer=self.user)
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('edit-event', args=[event.id]))
        self.assertEqual(response.status_code, 200)

    def test_edit_event_view_form_submission(self):
        event = Event.objects.create(name='Test Event', description='This is a test event', organizer=self.user)
        self.client.login(username='testuser', password='testpassword')
        data = {
            'name': 'Updated Event',
            'description': 'This is an updated event',
            'organizer': self.user.id
        }
        response = self.client.post(reverse('edit-event', args=[event.id]), data)
        self.assertEqual(response.status_code, 302)

    def test_delete_event_view_for_authenticated_user(self):
        event = Event.objects.create(name='Test Event', description='This is a test event', organizer=self.user)
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('delete-event', args=[event.id]))
        self.assertEqual(response.status_code, 200)

    def test_delete_event_view_form_submission(self):
        event = Event.objects.create(name='Test Event', description='This is a test event', organizer=self.user)
        self.client.login(username='testuser', password='testpassword')
        response = self.client.post(reverse('delete-event', args=[event.id]))
        self.assertEqual(response.status_code, 302) 


## GROUP SECTION ###

## TO DO ###

## PLAYER SECTION ###

## TO DO ###

## functions from views.py ###

class RegisterViewTests(TestCase):
    def test_register_view_available(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)

    def test_register_user_with_existing_username(self):
        User.objects.create_user('testuser', 'test@example.com', 'testpassword123')

        data = {
            'username': 'testuser',
            'password1': 'testpassword123',
            'password2': 'testpassword123',
        }
        response = self.client.post(reverse('register'), data)
        self.assertEqual(response.status_code, 200)

        self.assertEqual(User.objects.filter(username='testuser').count(), 1)


class SuccessViewTests(TestCase):
    def test_success_view_available(self):
        response = self.client.get(reverse('success'))
        self.assertEqual(response.status_code, 200)

class SecretSantaTests(TestCase):

    def test_secret_santa_no_participants(self):
        participants = []
        max_price = 50
        currency = 'USD'
        date = '2023-12-25'

        secret_santa(participants, max_price, currency, date)

        self.assertEqual(len(mail.outbox), 0)

    def test_secret_santa_valid_participants(self):
        participants = [
            ('A', 'a@example.com'),
            ('B', 'b@example.com'),
            ('C', 'c@example.com'),
        ]
        max_price = 50
        currency = 'USD'
        date = '2023-12-25'

        random.seed(42)

        secret_santa(participants, max_price, currency, date)

        self.assertEqual(len(mail.outbox), len(participants))

        for i, (name, email) in enumerate(participants):
            expected_subject = 'Secret Santa'
            expected_message = f'Hi {name},\n\nYou are {participants[(i+1)%len(participants)][0]}\'s Secret Santa!'
            expected_message += f'\n\nThe maximum price for gifts is {max_price} {currency}.'
            expected_message += f'\nThe exchange date is {date}.'
            expected_message += f'\n\nBest wishes,\nSecret Santa'
            self.assertEqual(mail.outbox[i].subject, expected_subject)
            self.assertEqual(mail.outbox[i].body, expected_message)