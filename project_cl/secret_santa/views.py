from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.views import View
from .forms import GameForm
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
        form = GameForm(request.POST)
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
        else:
            return HttpResponse("error")


# def secret_santa(participants, max_price, currency):
#     smtp_server = 'smtp.gmail.com'
#     smtp_port = 587
#     smtp_username = 'harribo4ever@gmail.com'
#     smtp_password = 'btpo azqj dvqz srun'
#     from_email = 'harribo4ever@gmail.com'

#     random.shuffle(participants)
#     for i in range(len(participants)):
#         giver_name, giver_email = participants[i]
#         nex_index = (i+1) % len(participants)
#         receiver_name, receiver_email = participants[nex_index]

#         subject = 'Secret Santa'
        # message = f'Hi {giver_name},\n\nYou are {receiver_name}\'s Secret Santa!\n\nBest wishes,\nSecret Santa'

#         msg = MIMEText(message)
#         msg['Subject'] = subject
#         msg['From'] = from_email
#         msg['To'] = giver_email

#         try:
#             server = smtplib.SMTP(smtp_server, smtp_port)
#             server.starttls()
#             server.login(smtp_username, smtp_password)
#             server.sendmail(from_email, [giver_email], msg.as_string())
#             print(f'Successfully sent email to {giver_email}')

#         except Exception as error:
#             print(f'Error sendong email to {giver_email}: {error}')

#         finally:
#             server.quit()

def secret_santa(participants, max_price, currency):
    random.shuffle(participants)
    for i in range(len(participants)):
        giver_name, giver_email = participants[i]
        next_index = (i+1) % len(participants)
        receiver_name, receiver_email = participants[next_index]
        
        subject = 'Secret Santa'
        message = f'Hi {giver_name},\n\nYou are {receiver_name}\'s Secret Santa!\n\nBest wishes,\nSecret Santa'
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [giver_email]
        send_mail(subject, message, email_from, recipient_list)
        print(f'Successfully sent email to {giver_email}')
