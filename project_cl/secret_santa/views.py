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


# add register option

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


class QuickGameView(View):
    def get(self, request):
        form = GameForm()
        return render(request, 'quick_game.html', {'form': form})

    def post(self, request):
        return HttpResponse('OK')
    # moze zrobic tak, że klikniecie przycisku spowoduje przejscie do widoku podsumowujacego, z mozlwoscia edyci, a potem bedzie kod z wysylaniem maili?
