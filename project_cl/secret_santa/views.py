from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from .forms import EventForm, GameForm, GroupForm, ParticipantForm, QucikGameForm
from .models import Event, GiftPair, Group, Participant
import random
# import smtplib
# from email.mime.text import MIMEText
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth import authenticate, login, logout


class MainView(View):
    def get(self, request):
        return render(request, 'index.html')


class LoginView(View):
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
            return HttpResponse("error")


class LogoutView(View):
    def get(self, request):
        logout(request)
        return render(request, "index.html")


class BaseView(View): # this view is just temporary - will be deleted later
    def get(self, request):
        user = request.user
        return render(request, "base.html", {'user': user}) # base meaning logged user view - main view for logged user!


class LoggedUserView(View):
    def get(self, request):
        user = request.user
        events = Event.objects.filter(organizer=user)
        groups = Group.objects.filter(creator=user)
        players = Participant.objects.filter(creator=user)
        return render(request, "logged_user.html", {'user': user, 'events': events, 'groups': groups, 'players': players})


class QuickGameView(View):
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
                players_name = request.POST.get(f'player_name_{i}')
                players_email = request.POST.get(f'player_email_{i}')
                participants.append((players_name, players_email))

            secret_santa(participants, max_price, currency, date)

            return HttpResponse("success") # need another view with congrats and maybe summary if you input an email
        else:
            return HttpResponse("error")

        # maybe add custon message that user can see when inputing
        # when email spelled incoreccly by user - need a msg but there is a problem because it is JS not forms!!!
        # valitation error - need to add it to forms.py


def secret_santa(participants, max_price, currency, date):
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
        print(f'Successfully sent email to {giver_email}')

        # many mails sending is time consuming - work on this later


class AddEventView(View):
    def get(self, request):
        form = EventForm()
        return render(request, 'add_event.html', {'form': form})

    def post(self, request):
        form = EventForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('base')
        else:
            return HttpResponse("error")


class EditEventView(View):
    def get(self, request, event_id):
        event = Event.objects.get(pk=event_id)
        form = EventForm(instance=event)
        return render(request, 'edit_event.html', {'form': form})

    def post(self, request, event_id):
        event = Event.objects.get(pk=event_id)
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            return redirect('base')
        else:
            return HttpResponse("error")


class DeleteEventView(View):
    def get(self, request, event_id):
        event = get_object_or_404(Event, pk=event_id)
        return render(request, 'event_delete.html', {'event': event})

    def post(self, request, event_id):
        event = get_object_or_404(Event, pk=event_id)
        event.delete()
        return redirect('base')


class AddGroupView(View):
    def get(self, request):
        form = GroupForm()
        return render(request, 'add_group.html', {'form': form})

    def post(self, request):
        form = GroupForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('base')
        else:
            return HttpResponse("error")


class EditGroupView(View):
    def get(self, request, group_id):
        group = Group.objects.get(pk=group_id)
        form = GroupForm(instance=group)
        return render(request, 'edit_group.html', {'form': form})

    def post(self, request, group_id):
        group = Group.objects.get(pk=group_id)
        form = GroupForm(request.POST, instance=group)
        if form.is_valid():
            form.save()
            return redirect('base')
        else:
            return HttpResponse("error")


class DeleteGroupView(View):
    def get(self, request, group_id):
        group = get_object_or_404(Group, pk=group_id)
        return render(request, 'group_delete.html', {'group': group})

    def post(self, request, group_id):
        group = get_object_or_404(Group, pk=group_id)
        group.delete()
        return redirect('base')


class AddPlayerView(View):
    def get(self, request):
        form = ParticipantForm()
        return render(request, 'add_player.html', {'form': form})

    def post(self, request):
        form = ParticipantForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('base')
        else:
            return HttpResponse("error")


class EditPlayerView(View):
    def get(self, request, player_id):
        player = Participant.objects.get(pk=player_id)
        form = ParticipantForm(instance=player)
        return render(request, 'edit_player.html', {'form': form})

    def post(self, request, player_id):
        player = Participant.objects.get(pk=player_id)
        form = ParticipantForm(request.POST, instance=player)
        if form.is_valid():
            form.save()
            return redirect('base')
        else:
            return HttpResponse("error")


class DeletePlayerView(View):
    def get(self, request, player_id):
        player = get_object_or_404(Participant, pk=player_id)
        return render(request, 'player_delete.html', {'player': player})

    def post(self, request, player_id):
        player = get_object_or_404(Participant, pk=player_id)
        player.delete()
        return redirect('base')


class GameView(View):
    def get(self, request):
        form = GameForm()
        return render(request, 'game.html', {'form': form})

    def post(self, request):
        form = GameForm(request.POST)
        if form.is_valid():
            event = form.cleaned_data['event']
            group = form.cleaned_data['group']
            participants = [(participant.name, participant.email) for participant in group.participants.all()]
            max_price = group.price_limit
            currency = group.currency
            date = group.exchange_date

            # secret santa function logic
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
                )
                gift_pair.save()

                # sending emails logic

                subject = 'Secret Santa'
                message = f'Hi {giver.name},\n\nYou are {receiver.name}\'s Secret Santa!'
                message += f'\n\nThe maximum price for gifts is {max_price} {currency}.'
                message += f'\nThe exchange date is {date}.'
                message += f'\n\nBest wishes,\nSecret Santa'
                email_from = settings.EMAIL_HOST_USER
                recipient_list = [giver.email]
                send_mail(subject, message, email_from, recipient_list)

            return redirect('gift-pairs', group_id=group.id)
        else:
            return HttpResponse("error")


class GiftPairs(View):
    def get(self, request, group_id):
        group = get_object_or_404(Group, pk=group_id)
        gift_pairs = GiftPair.objects.filter(group=group)
        return render(request, 'gift_pairs.html', {'gift_pairs': gift_pairs})



# must:
# detail view for event / group / participant?
# my games / games i participate in OR NOT MAYBE PO PROSTU NA STORNIE WSZYTSKIE INFORMACJE ŁADNIE PODANE W LOGGED, a do groups "wyniki"
# game form / mew draw
# register

# maybe:
# change password
# custom message?
# delete account
# change email
# change username
# view with results for email (if simmilar to games i participate in - then it is a must)