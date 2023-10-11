from datetime import date
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views import View
from .forms import (CustomPasswordResetForm, EmailLookupForm, EventForm,
                    GameForm, GroupForm, ParticipantForm,
                    QucikGameForm, RegisterForm)
from .models import Event, GiftPair, Group, Participant
import random
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.views import PasswordChangeView
from django.views.generic.edit import DeleteView
from django.contrib.auth.models import User
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator


### MAIN VIEW AND ITS' OPTIONS SECTION ###


class MainView(View):
    """
    First view after entering the website.

    Methods:
        - get(self, request): Handles GET requests and renders the index.html template.
    """
    def get(self, request):
        return render(request, 'index.html')


class QuickGameView(View):
    """
    View implementing quick game option.

    Methods:
        - get(self, request): Handles GET requests and renders the quick game form.
        - post(self, request): Handles POST requests and processes the quick game data,
                              including validation and Secret Santa assignment.
    """
    def get(self, request):
        form = QucikGameForm()
        return render(request, 'quick_game.html', {'form': form})

    def post(self, request):
        form = QucikGameForm(request.POST)
        if form.is_valid():
            max_price = form.cleaned_data['max_price']
            currency = form.cleaned_data['currency']
            date = form.cleaned_data['date']
            num_players = int(request.POST.get('num_players', 0))

            participants = []
            for i in range(1, num_players + 1):
                player_name = request.POST.get(f'player_name_{i}')
                player_email = request.POST.get(f'player_email_{i}')
                if not player_name or not player_email or '@' not in player_email:
                    return HttpResponse("error: Invalid player data")

                participants.append((player_name, player_email))

            secret_santa(participants, max_price, currency, date)

            # return HttpResponse("All emails have been successfully sent! Enjoy your `Secret Santa` game!") # succes page with back btn
            return redirect('success')
        else:
            return HttpResponse("error: Invalid form data")


def secret_santa(participants, max_price, currency, date):
    """
    Function created for running secret santa function.
    Shuffles results are not saved into database.

    :param participants: list of tuples (name, email)
    :param max_price: maximum price for gifts
    :param currency: currency of max_price
    :param date: date of gift exchange
    """
    random.shuffle(participants)
    for i in range(len(participants)):
        giver_name, giver_email = participants[i]
        next_index = (i+1) % len(participants)
        receiver_name, receiver_email = participants[next_index]

        subject = 'Secret Santa'
        message = f'Hi {giver_name},\n\nYou are {receiver_name}\'s Secret Santa!'
        message += f'\n\nThe maximum price for gifts is {max_price} {currency}.'
        message += f'\nThe exchange date is {date}.'
        message += f'\n\nBest wishes,\nSecret Santa'
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [giver_email]
        send_mail(subject, message, email_from, recipient_list)


class LoginView(View):
    """
    View for user login.

    Methods:
        - get(self, request): Handles GET requests for the login page.
        - post(self, request): Handles POST requests for user login.
    """
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('base')
        return render(request, "login_user_view.html")

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('base')
        else:
            return HttpResponse("Your login data was invalid. Please try again.")


class LogoutView(View):
    """
    View for user logout.

    Methods:
        - get(self, request): Handles GET requests for user logout.
    """
    def get(self, request):
        logout(request)
        return render(request, "index.html")


class ChangePassword(PasswordChangeView):
    """
    View for changing user password.
    """
    template_name = 'change_password.html'
    success_url = '/login/'


class DeleteAccountView(SuccessMessageMixin, DeleteView):
    """
    View for deleting user account.
    """
    model = User
    template_name = 'user_delete_confirm.html'
    success_message = 'Your account has been deleted.'
    success_url = reverse_lazy('index')


def register(request):
    """
    Function for registering new users.
    """
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})


class LoggedUserView(View):
    def get(self, request):
        user = request.user
        events = Event.objects.filter(organizer=user)
        groups = Group.objects.filter(creator=user)
        players = Participant.objects.filter(creator=user)
        gift_pairs = GiftPair.objects.filter(event__organizer=user)
        events_with_draws = Event.objects.filter(giftpair__in=gift_pairs).distinct()
        game_numbers = list(gift_pairs.values_list('game_number', flat=True).distinct())

        game_data = []
        for game_number in game_numbers:
            game_pairs = gift_pairs.filter(game_number=game_number)
            game_info = {
                'game_number': game_number,
                'group_name': game_pairs[0].group.name,
                'event_name': game_pairs[0].event.name,
                'date': game_pairs[0].date,
                'price_limit': game_pairs[0].group.price_limit,
                'pairs': game_pairs.values('giver__first_name', 'giver__last_name', 'receiver__first_name', 'receiver__last_name')

            }
            game_data.append(game_info)

        return render(request, "logged_user.html", {
            'user': user,
            'events': events,
            'groups': groups,
            'players': players,
            'gift_pairs': gift_pairs,
            'events_with_draws': events_with_draws,
            'game_data': game_data,  # Przekazujemy dane o grach do szablonu
        })


### EVENT SECTION ###


@method_decorator(login_required, name='dispatch')
class AddEventView(View):
    """
    View for adding new events.

    Methods:
        - get(self, request): Handles GET requests and renders the add_event.html template.
        - post(self, request): Handles POST requests and processes the event data,
    """
    def get(self, request):
        form = EventForm(user=request.user)
        return render(request, 'add_event.html', {'form': form})

    def post(self, request):
        form = EventForm(request.POST, user=request.user)
        try:
            if form.is_valid():
                form.save()
                return redirect('base')
        except Exception as e:
            return HttpResponse(f"Erorr occured: {e}. Please try again.")

        return HttpResponse("An error occurred. Please try again.")


class EditEventView(View):
    """
    View for editing existing events.

    Methods:
        - get(self, request, event_id): Handles GET requests and renders the edit_event.html template.
        - post(self, request, event_id): Handles POST requests and processes the event data,
    """
    def get(self, request, event_id):
        event = Event.objects.get(pk=event_id)
        form = EventForm(instance=event, user=request.user)
        return render(request, 'edit_event.html', {'form': form})

    def post(self, request, event_id):
        event = Event.objects.get(pk=event_id)
        form = EventForm(request.POST, instance=event, user=request.user)
        try:
            if form.is_valid():
                form.save()
                return redirect('base')
        except Exception as e:
            return HttpResponse(f"Erorr occured: {e}. Please try again.")

        return HttpResponse("An error occurred. Please try again.")


class DeleteEventView(View):
    """
    View for deleting existing events.

    Methods:
        - get(self, request, event_id): Handles GET requests and renders the event_delete.html template.
        - post(self, request, event_id): Handles POST requests and deletes the event.
    """
    def get(self, request, event_id):
        event = get_object_or_404(Event, pk=event_id)
        return render(request, 'event_delete.html', {'event': event})

    def post(self, request, event_id):
        try:
            event = get_object_or_404(Event, pk=event_id)
            event.delete()
            return redirect('base')
        except Exception as e:
            return HttpResponse(f"An error occurred: {e}. Please try again.")


### GROUP SECTION ###


@method_decorator(login_required, name='dispatch')
class AddGroupView(View):
    """
    View for adding new groups.

    Methods:
        - get(self, request): Handles GET requests and renders the add_group.html template.
        - post(self, request): Handles POST requests and processes the group data.
    """
    def get(self, request):
        form = GroupForm(user=request.user)
        return render(request, 'add_group.html', {'form': form})

    def post(self, request):
        try:
            form = GroupForm(request.POST, user=request.user)
            if form.is_valid():
                form.save()
                return redirect('base')
        except Exception as e:
            return HttpResponse(f"An error occurred: {e}. Please try again.")
        return HttpResponse("An error occurred. Please try again.")


class EditGroupView(View):
    """
    View for editing existing groups.

    Methods:
        - get(self, request, group_id): Handles GET requests and renders the edit_group.html template.
        - post(self, request, group_id): Handles POST requests and updates the group data.
    """
    def get(self, request, group_id):
        group = Group.objects.get(pk=group_id)
        form = GroupForm(instance=group, user=request.user)
        return render(request, 'edit_group.html', {'form': form})

    def post(self, request, group_id):
        try:
            group = Group.objects.get(pk=group_id)
            form = GroupForm(request.POST, instance=group, user=request.user)
            if form.is_valid():
                form.save()
                return redirect('base')
        except Exception as e:
            return HttpResponse(f"An error occurred: {e}. Please try again.")
        return HttpResponse("An error occurred. Please try again.")


class DeleteGroupView(View):
    """
    View for deleting existing groups.

    Methods:
        - get(self, request, group_id): Handles GET requests and renders the group_delete.html template.
        - post(self, request, group_id): Handles POST requests and deletes the group.
    """
    def get(self, request, group_id):
        group = get_object_or_404(Group, pk=group_id)
        return render(request, 'group_delete.html', {'group': group})

    def post(self, request, group_id):
        try:
            group = get_object_or_404(Group, pk=group_id)
            group.delete()
            return redirect('base')
        except Exception as e:
            return HttpResponse(f"An error occurred: {e}. Please try again.")


### PLAYER SECTION ###


class AddPlayerView(View):
    """
    View for adding new players.

    Methods:
        - get(self, request): Handles GET requests and renders the add_player.html template.
        - post(self, request): Handles POST requests and processes the player data.
    """
    def get(self, request):
        form = ParticipantForm(user=request.user)
        return render(request, 'add_player.html', {'form': form})

    def post(self, request):
        try:
            form = ParticipantForm(request.POST, user=request.user)
            if form.is_valid():
                form.save()
                return redirect('base')
        except Exception as e:
            return HttpResponse(f"An error occurred: {e}. Please try again.")
        return HttpResponse("An error occurred. Please try again.")


class EditPlayerView(View):
    """
    View for editing existing players.

    Methods:
        - get(self, request, player_id): Handles GET requests and renders the edit_player.html template.
        - post(self, request, player_id): Handles POST requests and updates the player data.
    """
    def get(self, request, player_id):
        player = Participant.objects.get(pk=player_id)
        form = ParticipantForm(instance=player, user=request.user)
        return render(request, 'edit_player.html', {'form': form})

    def post(self, request, player_id):
        try:
            player = Participant.objects.get(pk=player_id)
            form = ParticipantForm(request.POST, instance=player, user=request.user)
            if form.is_valid():
                form.save()
                return redirect('base')
        except Exception as e:
            return HttpResponse(f"An error occurred: {e}. Please try again.")
        return HttpResponse("An error occurred. Please try again.")


class DeletePlayerView(View):
    """
    View for deleting existing players.

    Methods:
        - get(self, request, player_id): Handles GET requests and renders the player_delete.html template.
        - post(self, request, player_id): Handles POST requests and deletes the player.
    """
    def get(self, request, player_id):
        player = get_object_or_404(Participant, pk=player_id)
        return render(request, 'player_delete.html', {'player': player})

    def post(self, request, player_id):
        try:
            player = get_object_or_404(Participant, pk=player_id)
            player.delete()
            return redirect('base')
        except Exception as e:
            return HttpResponse(f"An error occurred: {e}. Please try again.")


### MAIN GAME SECTION ###


class GameView(View):
    """
    View for creating and sending gift pairs.

    Methods:
        - get(self, request): Handles GET requests and renders the game.html template with a form.
        - post(self, request): Handles POST requests, creates gift pairs, and sends emails.
    """
    def get(self, request):
        form = GameForm(user=request.user)
        return render(request, 'game.html', {'form': form})

    def post(self, request):
        form = GameForm(request.POST, user=request.user)
        if form.is_valid():
            event = form.cleaned_data['event']
            group = form.cleaned_data['group']
            date = form.cleaned_data['date']
            participants = [(participant.name, participant.email) for participant in group.participants.all()]
            max_price = group.price_limit
            currency = group.currency

            game_number = GiftPair.objects.latest('id').id + 1 if GiftPair.objects.exists() else 1

            random.shuffle(participants)

            for i in range(len(participants)):
                giver_name, giver_email = participants[i]
                next_index = (i+1) % len(participants)
                receiver_name, receiver_email = participants[next_index]

                giver = Participant.objects.get(email=giver_email)
                receiver = Participant.objects.get(email=receiver_email)

                gift_pair = GiftPair(
                    giver=giver,
                    receiver=receiver,
                    event=event,
                    group=group,
                    date=date,
                    game_number=game_number
                )
                gift_pair.save()

                subject = 'Secret Santa'
                message = f'Hi {giver.name},\n\nYou are {receiver.name}\'s Secret Santa!'
                message += f'\n\nThe maximum price for gifts is {max_price} {currency}.'
                message += f'\nThe exchange date is {date}.'
                message += f'\n\nBest wishes,\nSecret Santa'
                email_from = settings.EMAIL_HOST_USER
                recipient_list = [giver.email]
                send_mail(subject, message, email_from, recipient_list)

            # return redirect('base')
            return redirect('success')
        
        else:
            return HttpResponse("An error occurred. Please try again")



class GiftPairs(View): # this view is not necessary
    """
    View for displaying gift pairs for given event.

    Methods:
        - get(self, request, event_id): Handles GET requests and renders the gift_pairs.html template.
    """
    def get(self, request, group_id):
        group = get_object_or_404(Group, pk=group_id)
        gift_pairs = GiftPair.objects.filter(group=group)
        return render(request, 'gift_pairs.html', {'gift_pairs': gift_pairs})


class MyGiftPairsView(View):
    """
    View for displaying gift pairs for logged user.

    Methods:
        - get(self, request): Handles GET requests and renders the my_gift_pairs.html template.
    """
    def get(self, request):
        today = date.today()
        user_email = request.user.email

        try:
            participant = Participant.objects.get(email=user_email)
            gift_pairs = GiftPair.objects.filter(giver=participant)
        except Participant.DoesNotExist:
            gift_pairs = []

        if not gift_pairs:
            return HttpResponse("Your email does not participate in any games yet.")

        return render(request, 'my_gift_pairs.html', {'gift_pairs': gift_pairs, 'today': today})


class LookupView(View):
    """
    View for looking up gift pairs for given email.

    Methods:
        - get(self, request): Handles GET requests and renders the lookup.html template.
        - post(self, request): Handles POST requests and processes the email data.
    """
    def get(self, requst):
        form = EmailLookupForm()
        return render(requst, 'lookup.html', {'form': form})

    def post(self, request):
        today = date.today()
        form = EmailLookupForm(request.POST)
        if form.is_valid():
            user_email = form.cleaned_data['email']
            try:
                participant = Participant.objects.get(email=user_email)
                gift_pairs = GiftPair.objects.filter(giver=participant)
            except participant.DoesNotExist:
                gift_pairs = []

            return render(request, 'lookup_result.html', {'gift_pairs': gift_pairs, 'participant': participant, 'today': today})

        return render(request, 'lookup.html', {'form': form})


def success_view(request):
    return render(request, 'success.html')


########### TO DO ############

# MUST DO:
# tests!!!
# python anywhere BUT POSTGRES IS NOT AVALIABLE IN FREE OPTION?? -> FIND ANOTHER SOLUTION
# desgin + description CLEAN UP + btns on pages


# MUST BUT NOT FIRST PRIO:
# ability to load cvs
# custom messages
# PSWRD reset 


# NOT NECESSERY:
# load screen when playing game
# reset password
# is model group even necessery? i can add more data fields to game form - but it is not very important
# what about people who want to check their games, but it was quick game and it is not saved in db? maybe model for quick game in db will solve it
