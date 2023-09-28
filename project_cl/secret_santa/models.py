from django.db import models
from django.contrib.auth.models import User


class Event(models.Model):
    name = models.CharField(max_length=64)
    date = models.DateField() # chyba jednak to do kosza
    description = models.TextField()
    organizer = models.ForeignKey(User, on_delete=models.CASCADE) # one:many relationship


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


class Gift(models.Model):
    name = models.CharField(max_length=64)
    receiver = models.ForeignKey(Participant, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)


class Group(models.Model):
    name = models.CharField(max_length=64)
    event = models.ForeignKey(Event, on_delete=models.CASCADE) # one:many relationship
    participants = models.ManyToManyField(Participant) # many:many relationship
    # draw_date = models.DateField() # propably will be deleted due to lack of option of choosing date of email sending
    exchange_date = models.DateField()
    price_limit = models.DecimalField(max_digits=6, decimal_places=2)


class GiftPair(models.Model):
    giver = models.ForeignKey(Participant, on_delete=models.CASCADE, related_name='gifts_given') # many:many relationship
    receiver = models.ForeignKey(Participant, on_delete=models.CASCADE, related_name='gifts_received') # many:many relationship
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)

    def __str__(self):
        return f'Giver: {self.giver} -> Receiver: {self.receiver} (In group: {self.group} for event: {self.event})'
