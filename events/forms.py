from django import forms
from .models import Event, Venue, Payment, Ticket
from django.core.exceptions import ValidationError

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = [
            'title',
            'description',
            'venue',
            'start_datetime',
            'end_datetime',
            'capacity'
        ]
        widgets = {
            'start_datetime': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_datetime': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        venue = cleaned_data.get('venue')
        start = cleaned_data.get('start_datetime')
        end = cleaned_data.get('end_datetime')
        capacity = cleaned_data.get('capacity')


        if venue and capacity and capacity > venue.capacity:
            raise ValidationError(
                f"Event capacity ({capacity}) cannot exceed venue capacity ({venue.capacity})."
            )


        if venue and start and end:
            conflicts = Event.objects.filter(
                venue=venue,
                start_datetime__lt=end,
                end_datetime__gt=start
            )

            if self.instance.id:
                conflicts = conflicts.exclude(id=self.instance.id)

            if conflicts.exists():
                raise ValidationError(
                    "Another event is already scheduled in this venue during the selected time."
                )

        if start and end and start >= end:
            raise ValidationError("Event end time must be after start time.")
        
        return cleaned_data



class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['payment_method', 'amount']
        widgets = {
            'payment_method': forms.Select(choices=[('card', 'Card'), ('cash', 'Cash')]),
            'amount': forms.NumberInput(attrs={'readonly': 'readonly'}),
        }

TICKET_TYPE_CHOICES = [
    ('standard', 'Standard'),
    ('vip', 'VIP'),
    ('premium', 'Premium'),
]

TICKET_PRICES = {
    'standard': 50.00,
    'vip': 100.00,
    'premium': 150.00,
}

class TicketForm(forms.ModelForm):
    ticket_type = forms.ChoiceField(choices=TICKET_TYPE_CHOICES)

    class Meta:
        model = Ticket
        fields = ['ticket_type']