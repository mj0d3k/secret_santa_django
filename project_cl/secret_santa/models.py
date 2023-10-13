from django.db import models
from django.contrib.auth.models import User


class Event(models.Model):
    """
    Model created for events.
    """
    name = models.CharField(max_length=64)
    description = models.TextField()
    organizer = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Participant(models.Model):
    """
    Model created for players that can be then assigned to a group.
    """
    first_name = models.CharField(max_length=64)
    last_name = models.CharField(max_length=64)
    email = models.EmailField()
    wishlist = models.TextField(blank=True, null=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, default=None)

    @property
    def name(self):
        return "{} {}".format(self.first_name, self.last_name)

    def __str__(self):
        return self.name


class Group(models.Model):
    """
    Model created for groups of players that can be used in a shuffle.
    """

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
    creator = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    participants = models.ManyToManyField(Participant)
    price_limit = models.DecimalField(max_digits=10, decimal_places=2, null=False)
    currency = models.CharField(
        max_length=3,
        choices=CURRENCY_CHOICES,
        default='PLN',
    )

    def __str__(self):
        return self.name


class GiftPair(models.Model):
    """
    Model containing shuffles results.
    """
    giver = models.ForeignKey(Participant, on_delete=models.CASCADE, related_name='gifts_given')
    receiver = models.ForeignKey(Participant, on_delete=models.CASCADE, related_name='gifts_received')
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    date = models.DateField()
    game_number = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f'Giver: {self.giver} -> Receiver: {self.receiver} (In group: {self.group} for event: {self.event})'
