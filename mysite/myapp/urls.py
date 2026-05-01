from django.urls import path
from . import views, views_admin

urlpatterns = [
    # ================= AUTH & HOME =================
    path('', views.homepage, name='homepage'),
    path('login/', views.login_page, name='login_page'),
    path('api/login/', views.login_user, name='login_user'),
    path('register/', views.register_page, name='register_page'),
    path('api/register/', views.register_user, name='register_user'),
    path('logout/', views.logout_user, name='logout'),

    # ================= PASSWORD RESET =================
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('forgot-success/', views.forgot_password_success, name='forgot_password_success'),
    path('reset/<uidb64>/<token>/', views.password_reset_confirm_view, name='password_reset_confirm'),
    path('reset-success/', views.password_reset_success, name='password_reset_success'),

    # ================= DASHBOARD & PROFILE =================
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/profile/', views.profile, name='profile'),
    path('dashboard/change-password/', views.change_password, name='change_password'),
    path('dashboard/renew-pass/', views.renew_pass, name='renew_pass'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    

    path('schedule/', views.schedule, name='schedule'),
    path('schedule/<int:schedule_id>/details/', views.schedule_details, name='schedule_details'),

    # ================= BOOKING & TICKETS =================
    path('my-bookings/', views.my_bookings, name='my_bookings'),
    path('booking/<str:booking_id>/', views.booking_detail, name='booking_detail'),
    path('cancel-booking/<str:booking_id>/', views.cancel_booking, name='cancel_booking'),
    
   
    path('book-ticket/<int:schedule_id>/', views.book_ticket, name='book_ticket'),
    
    path('check-seats/<int:schedule_id>/', views.check_seat_availability, name='check_seat_availability'),
    path('select-seats/<int:schedule_id>/', views.select_seats, name='select_seats'),
    path('confirm-booking/', views.confirm_booking, name='confirm_booking'),
    path('booking-confirmation/<str:booking_id>/', views.booking_confirmation, name='booking_confirmation'),
    path('bus-schedule/', views.bus_schedule, name='bus_schedule'),

    # ================= ADMIN DASHBOARD =================
    path('admin_page/dashboard/', views_admin.admin_dashboard, name='admin_dashboard'),

    # ================= ADMIN FLEET MANAGEMENT =================
    path('admin_page/fleet/', views_admin.admin_fleet, name='admin_fleet'),
    path('admin_page/api/get-bus/<int:bus_id>/', views_admin.admin_get_bus, name='admin_get_bus'),
    path('admin_page/api/add-bus/', views_admin.admin_add_bus, name='admin_add_bus'),
    path('admin_page/api/update-bus/<int:bus_id>/', views_admin.admin_update_bus, name='admin_update_bus'),
    path('admin_page/api/toggle-bus/<int:bus_id>/', views_admin.admin_toggle_bus_status, name='admin_toggle_bus'),
    path('admin_page/api/delete-bus/<int:bus_id>/', views_admin.admin_delete_bus, name='admin_delete_bus'),

    # ================= ADMIN ROUTE MANAGEMENT =================
    path('admin_page/routes/', views_admin.admin_routes, name='admin_routes'),
    path('admin_page/api/route/<int:route_id>/', views_admin.admin_route_detail, name='admin_route_detail'),
    path('admin_page/api/add-route/', views_admin.admin_add_route, name='admin_add_route'),
    path('admin_page/api/add-schedule/', views_admin.admin_add_schedule, name='admin_add_schedule'),
    path('admin_page/api/delete-route/<int:route_id>/', views_admin.admin_delete_route, name='admin_delete_route'),
    path('admin_page/api/toggle-schedule/<int:schedule_id>/', views_admin.admin_toggle_schedule_status, name='admin_toggle_schedule'),
    path('admin_page/api/delete-schedule/<int:schedule_id>/', views_admin.admin_delete_schedule, name='admin_delete_schedule'),

    # ================= ADMIN USER MANAGEMENT =================
    path('admin_page/users/', views_admin.admin_users, name='admin_users'),
    path('admin_page/api/delete-user/<int:user_id>/', views_admin.admin_delete_user, name='admin_delete_user'),

    # ================= ADMIN BOOKINGS MANAGEMENT =================
    path('admin_page/bookings/', views_admin.admin_bookings, name='admin_bookings'),
    path('admin_page/api/update-booking/<int:booking_id>/', views_admin.admin_update_booking_status, name='admin_update_booking'),

    # ================= ADMIN REVENUE =================
    path('admin_page/revenue/', views_admin.admin_revenue, name='admin_revenue'),

    # ================= ADMIN ALERTS & NOTIFICATIONS =================
    path('admin_page/alerts/', views_admin.admin_alerts, name='admin_alerts'),
    path('admin_page/notifications/', views_admin.admin_notifications, name='admin_notifications'),
]