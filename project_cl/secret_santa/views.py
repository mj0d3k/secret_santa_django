from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.views import View
from .forms import GameForm
# import random
# import smtplib
# from email.mime.text import MIMEText
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
        return redirect('base')


class BaseView(View):
    def get(self, request):
        user = request.user
        return render(request, "base.html", {'user': user})


class QuickGameView(View):
    def get(self, request):
        form = GameForm()
        return render(request, 'quick_game.html', {'form': form})

    def post(self, request):
        form = GameForm()
        if form.is_valid():
            max_price = form.cleaned_data['max_price']
            currency = form.cleaned_data['currency']
            num_players = int(request.POST.get('num_players', 0))
            
        participants = []
        for i in range(1, num_players + 1):
            players_name = request.POST.get(f'player_name_{i}')
            players_email = request.POST.get(f'player_email_{i}')
            participants.append((players_name, players_email))

        secret_santa(participants, max_price, currency)

        return HttpResponse("success")
    

def secret_santa(participants, max_price, currency):
    pass