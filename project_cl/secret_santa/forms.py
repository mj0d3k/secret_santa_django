from django import forms
from .models import Event, Group, Participant
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


CURRENCY_CHOICES = [
    ('USD', 'U.S. dollar (USD)'),
    ('EUR', 'Euro (EUR)'),
    ('JPY', 'Japanese yen (JPY)'),
    ('GBP', 'Sterling (GBP)'),
    ('CNY', 'Renminbi (CNY)'),
    ('AUD', 'Australian dollar (AUD)'),
    ('CAD', 'Canadian dollar (CAD)'),
    ('CHF', 'Swiss franc (CHF)'),
    ('HKD', 'Hong Kong dollar (HKD)'),
    ('SGD', 'Singapore dollar (SGD)'),
    ('SEK', 'Swedish krona (SEK)'),
    ('KRW', 'South Korean won (KRW)'),
    ('NOK', 'Norwegian krone (NOK)'),
    ('NZD', 'New Zealand dollar (NZD)'),
    ('INR', 'Indian rupee (INR)'),
    ('MXN', 'Mexican peso (MXN)'),
    ('TWD', 'New Taiwan dollar (TWD)'),
    ('ZAR', 'South African rand (ZAR)'),
    ('BRL', 'Brazilian real (BRL)'),
    ('DKK', 'Danish krone (DKK)'),
    ('PLN', 'Polish złoty (PLN)'),
    ('THB', 'Thai baht (THB)'),
    ('ILS', 'Israeli new shekel (ILS)'),
    ('IDR', 'Indonesian rupiah (IDR)'),
    ('CZK', 'Czech koruna (CZK)'),
    ('AED', 'UAE dirham (AED)'),
    ('TRY', 'Turkish lira (TRY)'),
    ('HUF', 'Hungarian forint (HUF)'),
    ('CLP', 'Chilean peso (CLP)'),
    ('SAR', 'Saudi riyal (SAR)'),
    ('PHP', 'Philippine peso (PHP)'),
    ('MYR', 'Malaysian ringgit (MYR)'),
    ('COP', 'Colombian peso (COP)'),
    ('RUB', 'Russian ruble (RUB)'),
    ('RON', 'Romanian leu (RON)'),
    ('PEN', 'Peruvian sol (PEN)'),
    ('BHD', 'Bahraini dinar (BHD)'),
    ('BGN', 'Bulgarian lev (BGN)'),
    ('ARS', 'Argentine peso (ARS)'),
]


class QucikGameForm(forms.Form):
    max_price = forms.DecimalField(label='Max price', decimal_places=2, min_value=0.01)
    currency = forms.ChoiceField(label='Currency', choices=CURRENCY_CHOICES, widget=forms.Select)
    date = forms.DateField(label='Date', widget=forms.TextInput(attrs={'placeholder': 'YYYY-MM-DD'}))


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = '__all__'
        widgets = {
            'date': forms.TextInput(attrs={'placeholder': 'YYYY-MM-DD'}),
        }

# class EventForm(forms.Form):
#     name = forms.CharField(max_length=64)
#     description = forms.CharField(widget=forms.Textarea)
#     date = forms.DateField(widget=forms.TextInput(attrs={'placeholder': 'YYYY-MM-DD'}))

#     class Meta:
#         model = Event
#         fields = ['name', 'description', 'date']


class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = '__all__'
        widgets = {
            'exchange_date': forms.TextInput(attrs={'placeholder': 'YYYY-MM-DD'}),
        }


class ParticipantForm(forms.ModelForm):
    class Meta:
        model = Participant
        fields = '__all__'


class GameForm(forms.Form):
    event = forms.ModelChoiceField(queryset=Event.objects.all())
    group = forms.ModelChoiceField(queryset=Group.objects.all())
    date = forms.DateField(widget=forms.TextInput(attrs={'placeholder': 'YYYY-MM-DD'}))


class RegisterForm(UserCreationForm):
    email = forms.EmailField(label='Email', required=True)
    first_name = forms.CharField(label='First name', required=True)
    last_name = forms.CharField(label='Last name', required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')


class EmailLookupForm(forms.Form):
    email = forms.EmailField(label='Enter your email', required=True)