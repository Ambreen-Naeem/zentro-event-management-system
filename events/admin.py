from django.contrib import admin
from .models import Users, Organizer, Attendee, Venue, Event, EventRegistration, Ticket, Payment

# --------------------------
# Users
# --------------------------
@admin.register(Users)
class UsersAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'role', 'is_superuser', 'is_staff')
    list_filter = ('role', 'is_superuser', 'is_staff')
    search_fields = ('username', 'email')

# --------------------------
# Organizer
# --------------------------
@admin.register(Organizer)
class OrganizerAdmin(admin.ModelAdmin):
    list_display = ('user', 'organization_name')
    search_fields = ('user__username', 'organization_name')

# --------------------------
# Attendee
# --------------------------
@admin.register(Attendee)
class AttendeeAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone')
    search_fields = ('user__username', 'phone')

# --------------------------
# Venue
# --------------------------
@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'capacity')
    search_fields = ('name', 'address')
    list_filter = ('capacity',)

# --------------------------
# Event
# --------------------------
@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'organizer', 'venue', 'start_datetime', 'end_datetime', 'status')
    search_fields = ('title', 'description', 'organizer__user__username')
    list_filter = ('status', 'venue')
    date_hierarchy = 'start_datetime'

# --------------------------
# Event Registration
# --------------------------
@admin.register(EventRegistration)
class EventRegistrationAdmin(admin.ModelAdmin):
    list_display = ('attendee', 'event', 'registration_datetime')
    search_fields = ('attendee__user__username', 'event__title')
    list_filter = ('event',)

# --------------------------
# Ticket
# --------------------------
@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('registration', 'ticket_type', 'price')
    search_fields = ('registration__attendee__user__username', 'ticket_type')

# --------------------------
# Payment
# --------------------------
@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('ticket', 'user', 'amount', 'payment_method', 'payment_datetime')
    search_fields = ('user__username', 'payment_method')
    list_filter = ('payment_method',)
    date_hierarchy = 'payment_datetime'
