from django.db import models
from django.contrib.auth.models import User


class Event(models.Model):
    name = models.CharField(max_length=64)
    date = models.DateField()
    description = models.TextField()
    organizer = models.ForeignKey(User, on_delete=models.CASCADE)


class Participant(models.Model):
    first_name = models.CharField(max_length=64)
    last_name = models.CharField(max_length=64)
    email = models.EmailField()
    wishlist = models.TextField(blank=True, null=True) # optional


class Gift(models.Model):
    name = models.CharField(max_length=64)
    receiver = models.ForeignKey(Participant, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)


class Group(models.Model):
    name = models.CharField(max_length=64)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    participants = models.ManyToManyField(Participant)
    draw_date = models.DateField()
    exchange_date = models.DateField()
    price_range = models.DecimalField(max_digits=6, decimal_places=2)


class GiftPair(models.Model):
    giver = models.ForeignKey(Participant, on_delete=models.CASCADE)
    receiver = models.ForeignKey(Participant, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)

    def __str__(self):
        return f'Giver: {self.giver} -> Receiver: {self.receiver} (In group: {self.group} for event: {self.event})'
