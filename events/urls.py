from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('logout/', views.logout_view, name='logout'),
    
    #Organizer
    path('events/create/', views.create_event, name='create_event'),
    path('events/my-events/', views.my_events, name='my_events'),
    path('events/my-events/edit/<int:event_id>/', views.edit_event, name='edit_event'),
    path('events/my-events/delete/<int:event_id>/', views.delete_event, name='delete_event'),
    path('my-events/cancel/<int:event_id>/', views.cancel_event, name='cancel_event'),
    path('dashboard/registrations/', views.organizer_registrations, name='organizer_registrations'),



    #Attendee
    path('browse-events/', views.browse_events, name='browse_events'),
    path('my-tickets/', views.my_tickets, name='my_tickets'),
    path('cancel-registration/<int:reg_id>/', views.cancel_registration, name='cancel_registration'),
    path('events/pay-ticket/<int:ticket_id>/', views.pay_ticket, name='pay_ticket'),
    path('register/<int:event_id>/', views.register_event, name='register_event'),
    path('events/<int:event_id>/registrations/', views.event_registrations, name='event_registrations'),
    
]

