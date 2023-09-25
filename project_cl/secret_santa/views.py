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
        pass
