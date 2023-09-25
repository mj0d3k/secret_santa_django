from django.http import HttpResponse
from django.shortcuts import render
from django.views import View
from .forms import GameForm


class MainView(View):
    def get(self, request):
        return render(request, 'index.html')


class QuickGameView(View):
    def get(self, request):
        form = GameForm()
        return render(request, 'quick_game.html', {'form': form})
    
    def post(self, request):
        form = GameForm(request.POST)
        if form.is_valid():
            print(form.cleaned_data)
        return HttpResponse('OK')
