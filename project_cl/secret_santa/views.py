from datetime import date
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views import View
from .forms import EmailLookupForm, EventForm, GameForm, GroupForm, ParticipantForm, QucikGameForm, RegisterForm
from .models import Event, GiftPair, Group, Participant
import random
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.views import PasswordChangeView
from django.views.generic.edit import DeleteView
# from django.contrib import messages
# from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator


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
        gift_pairs = GiftPair.objects.filter(event__organizer=user)
        events_with_draws = Event.objects.filter(giftpair__in=gift_pairs).distinct()
        return render(request, "logged_user.html", {
            'user': user,
            'events': events,
            'groups': groups,
            'players': players,
            'gift_pairs': gift_pairs,
            'events_with_draws': events_with_draws,
        })


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

            return HttpResponse("success")
        else:
            return HttpResponse("error")

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


@method_decorator(login_required, name='dispatch')
class AddEventView(View):
    def get(self, request):
        form = EventForm(user=request.user)
        return render(request, 'add_event.html', {'form': form})

    def post(self, request):
        form = EventForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()
            return redirect('base')
        else:
            return HttpResponse("error")


class EditEventView(View):
    def get(self, request, event_id):
        event = Event.objects.get(pk=event_id)
        form = EventForm(instance=event, user=request.user)
        return render(request, 'edit_event.html', {'form': form})

    def post(self, request, event_id):
        event = Event.objects.get(pk=event_id)
        form = EventForm(request.POST, instance=event, user=request.user)
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


@method_decorator(login_required, name='dispatch')
class AddGroupView(View):
    def get(self, request):
        form = GroupForm(user=request.user)
        return render(request, 'add_group.html', {'form': form})

    def post(self, request):
        form = GroupForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()
            # group = form.save()
            return redirect('base')
        else:
            return HttpResponse("error")


class EditGroupView(View):
    def get(self, request, group_id):
        group = Group.objects.get(pk=group_id)
        form = GroupForm(instance=group, user=request.user)
        return render(request, 'edit_group.html', {'form': form})

    def post(self, request, group_id):
        group = Group.objects.get(pk=group_id)
        form = GroupForm(request.POST, instance=group, user=request.user)
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
        form = ParticipantForm(user=request.user)
        return render(request, 'add_player.html', {'form': form})

    def post(self, request):
        form = ParticipantForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()
            return redirect('base')
        else:
            return HttpResponse("error")


class EditPlayerView(View):
    def get(self, request, player_id):
        player = Participant.objects.get(pk=player_id)
        form = ParticipantForm(instance=player, user=request.user)
        return render(request, 'edit_player.html', {'form': form})

    def post(self, request, player_id):
        player = Participant.objects.get(pk=player_id)
        form = ParticipantForm(request.POST, instance=player, user=request.user)
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
                    date=date
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
            #return render(request, 'game.html', {'form': form, 'date': date})
        else:
            return HttpResponse("error")


class GiftPairs(View): # hopefully will not be needed
    def get(self, request, group_id):
        group = get_object_or_404(Group, pk=group_id)
        gift_pairs = GiftPair.objects.filter(group=group)
        return render(request, 'gift_pairs.html', {'gift_pairs': gift_pairs})


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})


class ChangePassword(PasswordChangeView):
    template_name = 'change_password.html'
    success_url = '/login/'


class DeleteAccountView(SuccessMessageMixin, DeleteView):
    model = User
    template_name = 'user_delete_confirm.html'
    success_message = 'Your account has been deleted.'
    success_url = reverse_lazy('index')


class MyGiftPairsView(View):
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
    def get(self, requst):
        form = EmailLookupForm()
        return render(requst, 'lookup.html', {'form': form})

    def post(self, request):
        form = EmailLookupForm(request.POST)
        if form.is_valid():
            user_email = form.cleaned_data['email']
            try:
                participant = Participant.objects.get(email=user_email)
                gift_pairs = GiftPair.objects.filter(giver=participant)
            except participant.DoesNotExist:
                gift_pairs = []

            # return render(request, 'my_gift_pairs.html', {'gift_pairs': gift_pairs})
            return render(request, 'lookup_result.html', {'gift_pairs': gift_pairs})

        return render(request, 'lookup.html', {'form': form})

# TO DO:
# create special gmail account
# event names apprear more than once
# menu on logged user (part of design)



# tests
# validaton
# documentation

# ability to load cvs
# load screen when playing game
# desgin + description
# buttns if necesery
# reset password
# in event group and player add creator automatically
# custom messages
# what about people who want to check their games, but it was quick game and it is not saved in db? maybe model for quick game in db will solve it
# is model group even necessery? i can add more data fields to game form - but it is not very important
# python anywhere