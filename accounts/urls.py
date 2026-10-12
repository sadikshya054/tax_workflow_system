from django.urls import path
from . import views


urlpatterns = [

    # Displays the login page.
    path('login/', views.login_view, name='login'),

    # Allows logged-in users to change their password.
    path('change-password/', views.change_password, name='change_password'),

    # Displays confirmation after the password is changed.
    path('password-changed/', views.password_changed, name='password_changed'),
   
    # Ends the current user's session.
    path('logout/', views.logout_view, name='logout'),

    # Sends /dashboard/ to our role-based dashboard view.
    path('dashboard/', views.dashboard, name='dashboard'),

    # Dashboard restricted to Staff users.
    path('staff-dashboard/', views.staff_dashboard, name='staff_dashboard'),

    # Dashboard restricted to Client users.
    path('client-dashboard/', views.client_dashboard, name='client_dashboard'),

    # Opens the Staff Client list page.
    path('staff/clients/', views.staff_clients, name='staff_clients'),

    # Opens the selected Client's Tax Returns.
    path('staff/clients/<int:client_id>/tax-returns/', views.staff_client_tax_returns, name='staff_client_tax_returns'),   
]

