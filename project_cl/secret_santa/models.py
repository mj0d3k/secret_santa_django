from django.db import models
from django.contrib.auth.models import User


class Event(models.Model):
    name = models.CharField(max_length=64)
    #date = models.DateField() # chyba jednak to do kosza
    description = models.TextField()
    organizer = models.ForeignKey(User, on_delete=models.CASCADE) # one:many relationship

    def __str__(self):
        return self.name


class Participant(models.Model):
    first_name = models.CharField(max_length=64)
    last_name = models.CharField(max_length=64)
    email = models.EmailField()
    wishlist = models.TextField(blank=True, null=True) # optional
    creator = models.ForeignKey(User, on_delete=models.CASCADE, default=None) # one:many relationship

    @property
    def name(self):
        return "{} {}".format(self.first_name, self.last_name)

    def __str__(self):
        return self.name


class Gift(models.Model): # WILL BE DELETED LATER PROPABLY?
    name = models.CharField(max_length=64)
    receiver = models.ForeignKey(Participant, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)


class Group(models.Model):

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

    name = models.CharField(max_length=64)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, default=1) # one:many relationship
    #event = models.ForeignKey(Event, on_delete=models.CASCADE) # one:many relationship
    participants = models.ManyToManyField(Participant) # many:many relationship
    exchange_date = models.DateField()
    price_limit = models.DecimalField(max_digits=6, decimal_places=2)
    currency = models.CharField(
        max_length=3,
        choices=CURRENCY_CHOICES,
        default='PLN',
    )

    def __str__(self):
        return self.name


class GiftPair(models.Model):
    giver = models.ForeignKey(Participant, on_delete=models.CASCADE, related_name='gifts_given') # many:many relationship
    receiver = models.ForeignKey(Participant, on_delete=models.CASCADE, related_name='gifts_received') # many:many relationship
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)

    def __str__(self):
        return f'Giver: {self.giver} -> Receiver: {self.receiver} (In group: {self.group} for event: {self.event})'
