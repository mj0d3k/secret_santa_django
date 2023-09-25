from django.http import HttpResponse
from django.shortcuts import render
from django.views import View
from .forms import GameForm
import random
import smtplib
from email.mime.text import MIMEText


class MainView(View):
    def get(self, request):
        return render(request, 'index.html')


class QuickGameView(View):
    def get(self, request):
        form = GameForm()
        return render(request, 'quick_game.html', {'form': form})
    
    def post(self, request):
        return HttpResponse('OK')
    # moze zrobic tak, że klikniecie przycisku spowoduje przejscie do widoku podsumowujacego, z mozlwoscia edyci, a potem bedzie kod z wysylaniem maili?
