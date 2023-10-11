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
from secret_santa import views
#from django.contrib.auth import views as auth_views
from secret_santa.views import (MainView,
                                QuickGameView,
                                LoginView,
                                LogoutView,
                                LoggedUserView,
                                AddEventView,
                                AddGroupView,
                                AddPlayerView,
                                EditEventView,
                                EditGroupView,
                                EditPlayerView,
                                DeleteEventView,
                                DeleteGroupView,
                                DeletePlayerView,
                                GameView,
                                ChangePassword,
                                MyGiftPairsView,
                                LookupView,)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', MainView.as_view(), name='index'),
    path('quick-game/', QuickGameView.as_view(), name='quick_game'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('logged/', LoggedUserView.as_view(), name='base'),
    path('add-event/', AddEventView.as_view(), name='add-event'),
    path('edit-event/<int:event_id>/', EditEventView.as_view(), name='edit-event'),
    path('delete-event/<int:event_id>/', DeleteEventView.as_view(), name='delete-event'),
    path('add-group/', AddGroupView.as_view(), name='add-group'),
    path('edit-group/<int:group_id>/', EditGroupView.as_view(), name='edit-group'),
    path('delete-group/<int:group_id>/', DeleteGroupView.as_view(), name='delete-group'),
    path('add-player/', AddPlayerView.as_view(), name='add-player'),
    path('edit-player/<int:player_id>/', EditPlayerView.as_view(), name='edit-player'),
    path('delete-player/<int:player_id>/', DeletePlayerView.as_view(), name='delete-player'),
    path('new-game/', GameView.as_view(), name='new-game'),
    path('register/', views.register, name='register'),
    path('change-password/', ChangePassword.as_view(), name='change-password'),
    path('delete-account/<int:pk>/', views.DeleteAccountView.as_view(), name='delete_account'),
    path('my-gift-pairs/', MyGiftPairsView.as_view(), name='my-gift-pairs'),
    path('email-lookup/', LookupView.as_view(), name='email-lookup'),
    path('success/', views.success_view, name='success'),
    # path('reset-password/', CustomPasswrordResetView.as_view(), name='reset-pswrd'),
    # path('reset-password/confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
]
