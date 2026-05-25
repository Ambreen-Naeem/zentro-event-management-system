from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Users, Organizer, Attendee, Event, EventRegistration, Ticket
from django.http import HttpResponseForbidden
from .forms import EventForm, PaymentForm, TicketForm
from django.shortcuts import get_object_or_404
from django.db.models import Count, Q


TICKET_PRICES = {
    'standard': 50.00,
    'vip': 100.00,
    'premium': 150.00,
}


def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid username or password")

    return render(request, 'events/home.html')

def signup(request):
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        role = request.POST.get('role')
        phone = request.POST.get('phone')
        organization = request.POST.get('organization')


        if password1 != password2:
            messages.error(request, "Passwords do not match")
            return redirect('signup')

        if Users.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect('signup')
        
        if role == 'attendee' and not phone:
            messages.error(request, "Phone number is required for attendees.")
            return redirect('signup')

        if role == 'organizer' and not organization:
            messages.error(request, "Organization name is required for organizers.")
            return redirect('signup')

        user = Users.objects.create_user(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=password1,
            role=role
        )

        if role == 'organizer':
            Organizer.objects.create(
                user=user,
                organization_name=organization
            )

        elif role == 'attendee':
            Attendee.objects.create(
            user=user,
            phone=phone
        )

        messages.success(request, "Account created successfully! Please log in.")
        return redirect('home')

    return render(request, 'events/signup.html')


@login_required(login_url='home')
def dashboard(request):
    return render(request, 'events/dashboard.html')

from django.contrib import messages
from django.contrib.auth import logout
from django.shortcuts import redirect

def logout_view(request):
    logout(request)
    
    storage = messages.get_messages(request)
    for _ in storage:
        pass
    messages.info(request, "You have successfully logged out.")

    return redirect('home')


@login_required
def create_event(request):
    if request.user.role != 'organizer':
        return HttpResponseForbidden("You are not allowed to access this page.")

    organizer = Organizer.objects.get(user=request.user)

    if request.method == "POST":
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)

            if event.capacity > event.venue.capacity:
                messages.error(request, f"Event capacity cannot exceed venue capacity ({event.venue.capacity}).")
                return render(request, 'events/create_event.html', {'form': form})

            conflict = Event.objects.filter(
                venue=event.venue,
                start_datetime__lt=event.end_datetime,
                end_datetime__gt=event.start_datetime
            )
            if conflict.exists():
                messages.error(request, "Another event is already scheduled in this venue during the selected time.")
                return render(request, 'events/create_event.html', {'form': form})

            event.organizer = organizer
            event.status = 'scheduled'
            event.save()

            messages.success(request, f"Event '{event.title}' created successfully!")
            return redirect('my_events')
    else:
        form = EventForm()

    return render(request, 'events/create_event.html', {'form': form})


@login_required
def my_events(request):
    if request.user.role != 'organizer':
        return HttpResponseForbidden("You are not allowed to access this page.")

    organizer = Organizer.objects.get(user=request.user)

    events = (
        Event.objects
        .filter(organizer=organizer)
        .annotate(
            total_regs=Count('eventregistration', distinct=True),
            paid_regs=Count('eventregistration', filter=Q(eventregistration__ticket__payment__isnull=False), distinct=True),
            unpaid_regs=Count('eventregistration', filter=Q(eventregistration__ticket__payment__isnull=True), distinct=True),
        )
    )

    return render(request, 'events/my_events.html', {'events': events})


@login_required
def edit_event(request, event_id):
    if request.user.role != 'organizer':
        return HttpResponseForbidden("You are not allowed to access this page.")

    event = get_object_or_404(Event, id=event_id, organizer__user=request.user)

    if request.method == "POST":
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            updated_event = form.save(commit=False)

            if updated_event.capacity > updated_event.venue.capacity:
                messages.error(request, f"Event capacity cannot exceed venue capacity ({updated_event.venue.capacity}).")
                return render(request, 'events/edit_event.html', {'form': form, 'event': event})

            conflict = Event.objects.filter(
                venue=updated_event.venue,
                start_datetime__lt=updated_event.end_datetime,
                end_datetime__gt=updated_event.start_datetime
            ).exclude(id=event.id)

            if conflict.exists():
                messages.error(request, "Another event is already scheduled in this venue during the selected time.")
                return render(request, 'events/edit_event.html', {'form': form, 'event': event})

            # 3️⃣ Save
            updated_event.save()
            messages.success(request, f"Event '{updated_event.title}' updated successfully!")
            return redirect('my_events')
    else:
        form = EventForm(instance=event)

    return render(request, 'events/edit_event.html', {'form': form, 'event': event})


@login_required
def delete_event(request, event_id):
    if request.user.role != 'organizer':
        return HttpResponseForbidden("You are not allowed to access this page.")

    event = get_object_or_404(Event, id=event_id, organizer__user=request.user)

    if request.method == "POST":
        event.delete()
        messages.success(request, "Event deleted successfully!")
        return redirect('my_events')

    return render(request, 'events/delete_event.html', {'event': event})

@login_required
def cancel_event(request, event_id):
    if request.user.role != 'organizer':
        return HttpResponseForbidden("You are not allowed to access this page.")

    event = get_object_or_404(Event, id=event_id, organizer__user=request.user)

    if request.method == "POST":
        event.status = 'cancelled'
        event.save()
        messages.success(request, f"Event '{event.title}' has been cancelled.")
        return redirect('my_events')

    return render(request, 'events/cancel_event.html', {'event': event})

@login_required
def browse_events(request):
    if request.user.role != 'attendee':
        return HttpResponseForbidden("Only attendees can browse events.")

    events = Event.objects.filter(status='scheduled').order_by('start_datetime')

    attendee = Attendee.objects.get(user=request.user)

    registered_ids = EventRegistration.objects.filter(attendee=attendee).values_list('event_id', flat=True)

    return render(request, 'events/browse_events.html', {
        'events': events,
        'registered_ids': registered_ids
    })

@login_required
def my_tickets(request):
    if request.user.role != 'attendee':
        return HttpResponseForbidden("Only attendees can view tickets.")

    attendee = Attendee.objects.get(user=request.user)

    registrations = EventRegistration.objects.filter(attendee=attendee).prefetch_related('ticket_set')


    for reg in registrations:
        reg.ticket = reg.ticket_set.first()

    return render(request, 'events/my_tickets.html', {
        'registrations': registrations
    })


@login_required
def register_event(request, event_id):
    if request.user.role != 'attendee':
        return HttpResponseForbidden("Only attendees can register for events.")

    attendee = Attendee.objects.get(user=request.user)
    event = get_object_or_404(Event, id=event_id)


    current_regs = EventRegistration.objects.filter(event=event).count()
    if current_regs >= event.capacity:
        messages.error(request, "Sorry! This event is fully booked.")
        return redirect('browse_events')

    registration, created = EventRegistration.objects.get_or_create(
        attendee=attendee,
        event=event
    )

    TICKET_PRICES = {
        'standard': 50,
        'vip': 100,
        'premium': 150
    }

    if request.method == "POST":
        form = TicketForm(request.POST)
        if form.is_valid():
            ticket_type = form.cleaned_data['ticket_type']
            price = TICKET_PRICES[ticket_type]

            ticket, _ = Ticket.objects.update_or_create(
                registration=registration,
                defaults={
                    'ticket_type': ticket_type,
                    'price': price
                }
            )

            messages.success(request, f"Registration successful! You purchased a {ticket_type.upper()} ticket for ${price}.")
            return redirect('my_tickets')
    else:
        form = TicketForm(initial={'ticket_type': 'standard'})

    return render(request, 'events/register_event.html', {
        'form': form,
        'event': event,
        'ticket_prices': TICKET_PRICES
    })




@login_required
def cancel_registration(request, reg_id):
    if request.user.role != 'attendee':
        return HttpResponseForbidden("Only attendees can cancel registrations.")

    registration = get_object_or_404(EventRegistration, id=reg_id, attendee__user=request.user)

    registration.delete()
    messages.success(request, f"Your registration for {registration.event.title} has been cancelled.")
    return redirect('my_tickets')

@login_required
def pay_ticket(request, ticket_id):
    if request.user.role != 'attendee':
        return HttpResponseForbidden("Only attendees can pay for tickets.")

    ticket = get_object_or_404(Ticket, id=ticket_id, registration__attendee__user=request.user)

    if request.method == "POST":
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.ticket = ticket
            payment.user = request.user
            payment.save()
            messages.success(
                request,
                f"Payment of ${ticket.price} for {ticket.registration.event.title} successful!",
                extra_tags='payment'
            )
            return redirect('my_tickets')
    else:
        form = PaymentForm(initial={'amount': ticket.price})

    return render(request, 'events/pay_ticket.html', {'form': form, 'ticket': ticket})

@login_required
def event_registrations(request, event_id):
    if request.user.role != 'organizer':
        return HttpResponseForbidden("You are not allowed to access this page.")

    event = get_object_or_404(
        Event,
        id=event_id,
        organizer__user=request.user
    )

    registrations = (
    EventRegistration.objects
    .filter(event=event)
    .select_related('attendee__user')
    .prefetch_related('ticket_set')
)


    return render(request, 'events/event_registrations.html', {
        'event': event,
        'registrations': registrations
    })

@login_required
def organizer_registrations(request):
    if request.user.role != 'organizer':
        return HttpResponseForbidden("You are not allowed to access this page.")

    organizer = Organizer.objects.get(user=request.user)

    events = Event.objects.filter(organizer=organizer)

    registrations = (
        EventRegistration.objects
        .filter(event__in=events)
        .select_related('attendee__user', 'event')
        .prefetch_related('ticket_set__payment_set')
        .order_by('event__start_datetime')
    )

    return render(request, 'events/organizer_registrations.html', {
        'registrations': registrations,
        'organizer': organizer
    })
