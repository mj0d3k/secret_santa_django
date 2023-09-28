"""
URL configuration for project_cl project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from secret_santa.views import (MainView,
                                QuickGameView,
                                LoginView,
                                LogoutView,
                                LoggedUserView,
                                AddEventView,
                                AddGroupView,
                                AddPlayerView,
                                EditEventView,)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', MainView.as_view(), name='index'),
    path('quick-game/', QuickGameView.as_view(), name='quick_game'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('logged/', LoggedUserView.as_view(), name='base'),
    path('add-event/', AddEventView.as_view(), name='add-event'),
    path('edit-event/<int:event_id>/', EditEventView.as_view(), name='edit-event'),
    path('add-group/', AddGroupView.as_view(), name='add-group'),
    path('add-player/', AddPlayerView.as_view(), name='add-player'),
]
