from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models

class Users(AbstractUser):
    ROLE_CHOICES = [
        ('organizer', 'Organizer'),
        ('attendee', 'Attendee'),
        ('admin', 'Admin'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)


    groups = models.ManyToManyField(
        Group,
        related_name='custom_users_groups',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups'
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='custom_users_permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions'
    )

class Organizer(models.Model):
    user = models.OneToOneField(Users, on_delete=models.CASCADE)
    organization_name = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.user.username


class Attendee(models.Model):
    user = models.OneToOneField(Users, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return self.user.username


class Venue(models.Model):
    name = models.CharField(max_length=100, blank=False)
    address = models.CharField(max_length=200, blank=False)
    capacity = models.PositiveIntegerField(null=False, blank=False)

    def __str__(self):
        return self.name

class Event(models.Model):
    organizer = models.ForeignKey(Organizer, on_delete=models.CASCADE)
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.TextField()
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    capacity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField(max_length=20, default='scheduled')
    
    def __str__(self):
        return self.title


class EventRegistration(models.Model):
    attendee = models.ForeignKey(Attendee, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    registration_datetime = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('attendee', 'event')

class Ticket(models.Model):
    registration = models.ForeignKey(EventRegistration, on_delete=models.CASCADE)
    ticket_type = models.CharField(max_length=20)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    paid = models.BooleanField(default=False)


class Payment(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE)
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20)
    payment_datetime = models.DateTimeField(auto_now_add=True)
