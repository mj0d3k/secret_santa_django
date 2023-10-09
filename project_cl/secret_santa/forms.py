from django import forms
from .models import Event, Group, Participant
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import PasswordResetForm


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
    """
    Form created for quick game option.
    Allows to create shuffle when you are in a hurry.
    Results are not being saved in database.
    """
    max_price = forms.DecimalField(label='Max price', decimal_places=2, min_value=0.01)
    currency = forms.ChoiceField(label='Currency', choices=CURRENCY_CHOICES, widget=forms.Select)
    date = forms.DateField(label='Date', widget=forms.TextInput(attrs={'placeholder': 'YYYY-MM-DD'}))


class EventForm(forms.ModelForm):
    """"
    Form created for adding new events.
    """
    class Meta:
        model = Event
        fields = '__all__'
        widgets = {
            'date': forms.TextInput(attrs={'placeholder': 'YYYY-MM-DD'}),
            'organizer': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        """
        Method that allows to pass user as an argument.
        Organizer is now being automaticly added to the form (logged user).
        """
        user = kwargs.pop('user', None)
        super(EventForm, self).__init__(*args, **kwargs)
        if user:
            self.initial['organizer'] = user


class GroupForm(forms.ModelForm):
    """
    Form created for adding new groups.
    """
    class Meta:
        model = Group
        fields = '__all__'
        widgets = {
            'exchange_date': forms.TextInput(attrs={'placeholder': 'YYYY-MM-DD'}),
            'creator': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        """
        Method that allows to pass user as an argument.
        Creator is now being automaticly added to the form (logged user).
        User can only choose players from the list of their participants.
        """
        user = kwargs.pop('user', None)
        super(GroupForm, self).__init__(*args, **kwargs)
        if user:
            self.initial['creator'] = user
            self.fields['participants'].queryset = Participant.objects.filter(creator=user)

    def clean(self):
        """
        Method checking if created group contains at least 3 participants.
        """
        cleaned_data = super().clean()
        participants = cleaned_data.get('participants')
        if participants and len(participants) < 3:
            raise ValidationError('Group must contain at least 3 players.')


class ParticipantForm(forms.ModelForm):
    """
    Form created for adding new participants.
    """
    class Meta:
        model = Participant
        fields = '__all__'
        widgets = {
            'creator': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        """
        Method that allows to pass user as an argument.
        Creator is now being automaticly added to the form (logged user).
        """
        user = kwargs.pop('user', None)
        super(ParticipantForm, self).__init__(*args, **kwargs)
        if user:
            self.initial['creator'] = user


class GameForm(forms.Form):
    """
    Form created for creating new shuffle.
    """
    def __init__(self, user, *args, **kwargs):
        """
        Method that allows loggd user to choose 
        only from events and groups created by them.
        """
        super(GameForm, self).__init__(*args, **kwargs)
        self.fields['event'].queryset = Event.objects.filter(organizer=user)
        self.fields['group'].queryset = Group.objects.filter(creator=user)

    event = forms.ModelChoiceField(queryset=Event.objects.none())
    group = forms.ModelChoiceField(queryset=Group.objects.none())
    date = forms.DateField(widget=forms.TextInput(attrs={'placeholder': 'YYYY-MM-DD'}))


class RegisterForm(UserCreationForm):
    """
    Form created for registering new users.
    """
    email = forms.EmailField(label='Email', required=True)
    first_name = forms.CharField(label='First name', required=True)
    last_name = forms.CharField(label='Last name', required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')


class EmailLookupForm(forms.Form):
    """
    Form created for looking up shuffles results
    for a special email address.
    """
    email = forms.EmailField(label='Enter your email', required=True)


class CustomPasswordResetForm(PasswordResetForm): # not sure if I will include this view
    """
    Form created for resetting password.
    """
    email = forms.EmailField(
        label="Your Email",
        max_length=254,
        widget=forms.EmailInput(attrs={'autocomplete': 'email', 'class': 'form-control'})
    )
