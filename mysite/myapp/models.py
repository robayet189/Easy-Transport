from django.db import models
from django.contrib.auth.models import User
import random
import string


class UserProfile(models.Model):
    INSTITUTION_TYPES = [
        ('educational', 'Educational'),
        ('industrial', 'Industrial'),
    ]

    USER_TYPES = [
        ('student', 'Student'),
        ('faculty', 'Faculty'),
        ('staff', 'Staff'),
        ('admin', 'Admin'),
        ('driver', 'Driver'),
        ('executive', 'Executive'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='userprofile')
    phone = models.CharField(max_length=15, blank=True)
    institution_type = models.CharField(max_length=50, blank=True, choices=INSTITUTION_TYPES)
    user_type = models.CharField(max_length=20, choices=USER_TYPES, default='student')
    institution_id = models.CharField(max_length=50, blank=True)
    department = models.CharField(max_length=100, blank=True)
    is_pass_active = models.BooleanField(default=False)
    pass_valid_until = models.DateField(null=True, blank=True)
    pass_id = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} - {self.institution_id}"

    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"


class Route(models.Model):
    """Bus route information"""
    code = models.CharField(max_length=10, unique=True)
    start = models.CharField(max_length=100)
    end = models.CharField(max_length=100)
    distance_km = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.code}: {self.start} → {self.end}"

    class Meta:
        ordering = ['code']


class Bus(models.Model):
    """Bus details"""
    bus_number = models.CharField(max_length=20, unique=True)
    capacity = models.IntegerField(default=40)
    driver_name = models.CharField(max_length=100)
    driver_phone = models.CharField(max_length=15, blank=True)
    has_ac = models.BooleanField(default=False)
    has_wifi = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    last_maintenance = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.bus_number} - {self.driver_name}"

    class Meta:
        ordering = ['bus_number']


class Schedule(models.Model):
    """Bus schedule for specific dates"""
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name='schedules')
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE, related_name='schedules')
    departure_time = models.TimeField()
    arrival_time = models.TimeField(null=True, blank=True)
    travel_date = models.DateField()
    fare = models.DecimalField(max_digits=8, decimal_places=2, default=60.00)
    is_active = models.BooleanField(default=True)
    available_seats = models.IntegerField(default=40)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['route', 'travel_date', 'departure_time']
        ordering = ['travel_date', 'departure_time']

    def __str__(self):
        return f"{self.route.code} - {self.departure_time} on {self.travel_date}"

    @property
    def booked_seats(self):
        return self.bookings.filter(status='confirmed').aggregate(total=models.Sum('number_of_seats'))['total'] or 0

    @property
    def remaining_seats(self):
        return max(0, self.available_seats - self.booked_seats)


class Booking(models.Model):
    """Ticket booking information"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]

    PAYMENT_STATUS = [
        ('unpaid', 'Unpaid'),
        ('paid', 'Paid'),
        ('refunded', 'Refunded'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE, related_name='bookings')
    booking_date = models.DateTimeField(auto_now_add=True)
    number_of_seats = models.IntegerField(default=1)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='confirmed')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='paid')
    booking_id = models.CharField(max_length=50, unique=True, editable=False)
    passenger_name = models.CharField(max_length=100, blank=True)
    passenger_phone = models.CharField(max_length=15, blank=True)
    passenger_email = models.EmailField(max_length=100, blank=True)
    seat_numbers = models.CharField(max_length=200, blank=True)

    def save(self, *args, **kwargs):
        # Auto-generate unique booking_id if not set
        if not self.booking_id:
            while True:
                code = 'TR' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
                if not Booking.objects.filter(booking_id=code).exists():
                    self.booking_id = code
                    break
        # Auto-fill travel_date from schedule if not set
        if not hasattr(self, 'travel_date') or not self.travel_date:
            if self.schedule:
                self.travel_date = self.schedule.travel_date
        super().save(*args, **kwargs)

    def __str__(self):
        seat_info = f" - Seats: {self.seat_numbers}" if self.seat_numbers else ""
        return f"Booking {self.booking_id} - {self.passenger_name or self.user.username}{seat_info}"

    class Meta:
        ordering = ['-booking_date']
        verbose_name = "Booking"
        verbose_name_plural = "Bookings"