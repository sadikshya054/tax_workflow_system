from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404

from documents.models import Notification
from documents.models import TaxReturn, Document, Task
from .models import User

def login_view(request):
    # Redirect already authenticated users to their correct dashboard.
    if request.user.is_authenticated:
        if request.user.role == 'STAFF':
            return redirect('staff_dashboard')
        return redirect('client_dashboard')

    # Handles login requests submitted through the login form.
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Django securely checks the supplied login credentials.
        user = authenticate(
            request,
            username=username,
            password=password,
        )

        if user is not None:
            login(request, user)

            # Redirect users according to their system role.
            if user.role == 'STAFF':
                return redirect('staff_dashboard')

            return redirect('client_dashboard')

        return render(
            request,
            'accounts/login.html',
            {'error': 'Invalid username or password.'},
        )

    return render(request, 'accounts/login.html')

@login_required
def change_password(request):
    # Creates Django's built-in password change form.
    form = PasswordChangeForm(
        request.user,
        request.POST or None
    )

    if request.method == 'POST':

        # Checks the current and new password details.
        if form.is_valid():
            form.save()

            # Keeps the user logged in after changing the password.
            from django.contrib.auth import update_session_auth_hash

            update_session_auth_hash(
                request,
                form.user
            )

            return redirect('password_changed')

    return render(
        request,
        'accounts/change_password.html',
        {'form': form}
    )

@login_required
def password_changed(request):
    # Displays confirmation after the password is changed.
    return render(
        request,
        'accounts/password_changed.html'
    )

@login_required
def dashboard(request):
    # Shows a different message depending on the user's role.
    if request.user.role == 'STAFF':
        return HttpResponse('Staff Dashboard')

    return HttpResponse('Client Dashboard')

@login_required
def staff_dashboard(request):
    # Allows only Staff users to access this dashboard.
    if request.user.role != 'STAFF':
        return HttpResponse('Access denied.', status=403)

    # Counts Tax Returns waiting for Staff review.
    submitted_tax_returns = TaxReturn.objects.filter(
        status=TaxReturn.Status.SUBMITTED
    ).count()

    # Counts documents waiting for Staff review.
    submitted_documents = Document.objects.filter(
        status=Document.Status.SUBMITTED
    ).count()

    # Counts tasks that are still pending.
    pending_tasks = Task.objects.filter(
        status=Task.Status.PENDING
    ).count()

    # Gets the five most recently submitted Tax Returns for review.
    recent_tax_returns = TaxReturn.objects.filter(
        status=TaxReturn.Status.SUBMITTED
    ).select_related('client').order_by('-updated_at')[:5]

    # Gets the five most recently completed or discarded Tax Returns.
    recent_completed_tax_returns = TaxReturn.objects.filter(
        status__in=[
            TaxReturn.Status.COMPLETED,
            TaxReturn.Status.DISCARDED
    ]
).select_related('client').order_by('-updated_at')[:5]

    # Gets the five most recently reviewed documents.
    recent_reviewed_documents = Document.objects.filter(
        status=Document.Status.REVIEWED
    ).select_related('owner').order_by('-uploaded_at')[:5]

    # Gets the five most recently created Client tasks.
    recent_tasks = Task.objects.filter(
        assigned_to__role='CLIENT'
    ).select_related('assigned_to').order_by('-created_at')[:5]

    return render(
        request,
        'accounts/staff_dashboard.html',
        {
            'submitted_tax_returns': submitted_tax_returns,
            'submitted_documents': submitted_documents,
            'pending_tasks': pending_tasks,
            'recent_tax_returns': recent_tax_returns,
            'recent_completed_tax_returns': recent_completed_tax_returns,
            'recent_reviewed_documents': recent_reviewed_documents,
            'recent_tasks': recent_tasks,
        }
    )

@login_required
def staff_clients(request):
    # Only Staff users can access the Client list.
    if request.user.role != 'STAFF':
        return render(
            request,
            'documents/access_denied.html',
            status=403
        )

    # Gets all Client accounts for the Staff view.
    clients = User.objects.filter(
        role=User.Role.CLIENT
    ).order_by('username')

    return render(
        request,
        'accounts/staff_clients.html',
        {'clients': clients}
    )

@login_required
def staff_client_tax_returns(request, client_id):
    # Only Staff users can view a Client's Tax Returns.
    if request.user.role != 'STAFF':
        return render(
            request,
            'documents/access_denied.html',
            status=403
        )

    # Gets the selected Client account.
    client = get_object_or_404(
        User,
        id=client_id,
        role=User.Role.CLIENT
    )

    # Gets all Tax Returns belonging only to this Client.
    tax_returns = TaxReturn.objects.filter(
        client=client
    ).order_by('-updated_at')

    return render(
        request,
        'accounts/staff_client_tax_returns.html',
        {
            'client': client,
            'tax_returns': tax_returns,
        }
    )

@login_required
def client_dashboard(request):
    # Only Client users can access the Client Dashboard.
    if request.user.role != 'CLIENT':
        return render(
            request,
            'documents/access_denied.html',
            status=403
        )

    # Retrieves the Client's unread notifications.
    unread_notifications = Notification.objects.filter(
        recipient=request.user,
        is_read=False
    ).order_by('-created_at')

    # Retrieves the Client's recent notifications.
    notifications = Notification.objects.filter(
        recipient=request.user
    ).order_by('-created_at')[:10]

    return render(
        request,
        'accounts/client_dashboard.html',
        {
            'unread_notifications': unread_notifications,
            'notifications': notifications,
            'unread_count': unread_notifications.count()
        }
    )

@login_required
def logout_view(request):
    # Ends the user's authenticated session securely.
    logout(request)

    # Sends the user back to the login page.
    return redirect('login')

