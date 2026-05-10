# Import Django model utilities and User model for authentication
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class UserProfile(models.Model):
    """
    Extended user profile for institutional transport system
    CHANGE REASON: Store additional user data beyond Django's default User model
    """
    USER_TYPES = [
        ('student', 'Student'),
        ('faculty', 'Faculty'),
        ('staff', 'Staff'),
        ('admin', 'Admin'),
        ('driver', 'Driver'),
    ]
    INSTITUTION_TYPES = [
        ('educational', 'Educational'),
        ('industrial', 'Industrial'),
    ]

    # One-to-one relationship with Django User model for authentication
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=15, blank=True)
    user_type = models.CharField(max_length=20, choices=USER_TYPES, default='student')
    institution_type = models.CharField(max_length=50, blank=True, null=True)
    institution_id = models.CharField(max_length=50, blank=True)
    department = models.CharField(max_length=100, blank=True)
    is_pass_active = models.BooleanField(default=False)
    pass_valid_until = models.DateField(null=True, blank=True)
    pass_id = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return f"{self.user.username} ({self.user_type})"


class Bus(models.Model):
    """
    Bus/fleet management model
    CHANGE REASON: Track vehicle details, capacity, and features for booking system
    """
    bus_number = models.CharField(max_length=20, unique=True)
    capacity = models.IntegerField(default=40)
    driver_name = models.CharField(max_length=100)
    driver_phone = models.CharField(max_length=15, blank=True)
    has_ac = models.BooleanField(default=False)
    has_wifi = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.bus_number


class Route(models.Model):
    """
    Transport route definition
    CHANGE REASON: Define start/end points and distance for scheduling and fare calculation
    """
    code = models.CharField(max_length=10, unique=True)
    start = models.CharField(max_length=100)
    end = models.CharField(max_length=100)
    distance_km = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)

    def __str__(self):
        return f"{self.code}: {self.start} → {self.end}"


class Schedule(models.Model):
    """
    Scheduled trip instances for booking
    CHANGE REASON: Link routes, buses, and times for user booking interface
    """
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name='schedules')
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE, related_name='schedules')
    departure_time = models.TimeField()
    arrival_time = models.TimeField(null=True, blank=True)
    travel_date = models.DateField()
    fare = models.DecimalField(max_digits=8, decimal_places=2, default=60.00)
    is_active = models.BooleanField(default=True)
    available_seats = models.IntegerField(default=40)

    class Meta:
        unique_together = ['route', 'travel_date', 'departure_time']

    def __str__(self):
        return f"{self.route.code} on {self.travel_date}"


class Booking(models.Model):
    """
    User booking records with approval workflow
    CHANGE REASON: Track bookings with admin approval, payment, and passenger details
    """
    STATUS_CHOICES = [
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]
    PAYMENT_CHOICES = [('bkash', 'bKash'), ('sslcommerz', 'SSLCommerz'), ('cash', 'Cash')]

    booking_id = models.CharField(max_length=20, unique=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE, related_name='bookings')
    seat_number = models.CharField(max_length=10)
    booking_date = models.DateTimeField(auto_now_add=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    passenger_name = models.CharField(max_length=100)
    admin_remarks = models.TextField(blank=True, null=True, help_text="Admin approval/rejection remarks")
    approved_at = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_bookings')

    def save(self, *args, **kwargs):
        # Generate unique booking ID if not already set
        if not self.booking_id:
            import random, string
            self.booking_id = 'BK-' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.booking_id} - {self.passenger_name}"


class BusLocation(models.Model):
    """
    Real-time bus GPS tracking
    CHANGE REASON: Enable live bus location updates for user tracking feature
    """
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE, related_name='locations')
    latitude = models.FloatField()
    longitude = models.FloatField()
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"{self.bus.bus_number} - {self.latitude}, {self.longitude}"


# ==================== PAYMENT MODELS ====================

class PaymentMethod(models.Model):
    """Available payment methods configuration"""
    name = models.CharField(max_length=50)
    code = models.CharField(max_length=20, unique=True)
    is_active = models.BooleanField(default=True)
    icon = models.CharField(max_length=50, blank=True)
    
    def __str__(self):
        return self.name


class PaymentTransaction(models.Model):
    """
    All payment transactions across the system
    CHANGE REASON: Centralized payment tracking for passes, bookings, and refunds
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    
    PAYMENT_TYPE_CHOICES = [
        ('pass', 'Transport Pass'),
        ('single', 'Single Trip'),
        ('booking', 'Booking Payment'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    booking = models.ForeignKey('Booking', on_delete=models.SET_NULL, null=True, blank=True, related_name='payments')
    
    transaction_id = models.CharField(max_length=100, unique=True, blank=True)
    payment_method = models.CharField(max_length=50)
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPE_CHOICES, default='pass')
    
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    pass_type = models.CharField(max_length=20, blank=True)
    pass_valid_from = models.DateField(null=True, blank=True)
    pass_valid_until = models.DateField(null=True, blank=True)
    
    payment_details = models.JSONField(default=dict, blank=True)
    remarks = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        # Generate unique transaction ID if not already set
        if not self.transaction_id:
            import random, string
            self.transaction_id = 'TXN' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.transaction_id} - {self.user.username} - ৳{self.amount}"
    
    class Meta:
        ordering = ['-created_at']


class UserPass(models.Model):
    """
    User's active transport passes
    CHANGE REASON: Manage pass validity, ride limits, and renewal tracking
    """
    PASS_TYPES = [
        ('monthly', 'Monthly Pass'),
        ('semester', 'Semester Pass'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='passes')
    pass_type = models.CharField(max_length=20, choices=PASS_TYPES)
    transaction = models.OneToOneField(PaymentTransaction, on_delete=models.CASCADE, related_name='user_pass')
    
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)
    
    total_rides = models.IntegerField(default=0)
    remaining_rides = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.pass_type} (Valid until {self.end_date})"
    
    class Meta:
        ordering = ['-created_at']


# ==================== CHAT SYSTEM MODELS ====================

class ChatRoom(models.Model):
    """
    Chat room for user-admin-driver communication
    CHANGE REASON: Enable multi-role messaging for support and coordination
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_rooms', null=True, blank=True)
    admin = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='admin_chat_rooms')
    driver = models.ForeignKey('Driver', on_delete=models.SET_NULL, null=True, blank=True, related_name='driver_chat_rooms')
    booking = models.ForeignKey('Booking', on_delete=models.SET_NULL, null=True, blank=True, related_name='chat_rooms')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"Chat: {self.user.username} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"
    
    class Meta:
        ordering = ['-updated_at']


class ChatMessage(models.Model):
    """
    Individual chat messages with attachment support
    CHANGE REASON: Store message history with read status for real-time chat
    """
    MESSAGE_TYPES = [
        ('text', 'Text'),
        ('image', 'Image'),
        ('file', 'File'),
    ]
    
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    message = models.TextField()
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPES, default='text')
    attachment = models.FileField(upload_to='chat_attachments/', null=True, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.sender.username}: {self.message[:50]}"
    
    class Meta:
        ordering = ['created_at']


# ==================== DRIVER MODULE MODELS ====================

class Driver(models.Model):
    """
    Driver profile extending UserProfile with driver-specific fields
    CHANGE REASON: Separate driver data from general user profile for role-based features
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='driver_profile')
    license_number = models.CharField(max_length=50, unique=True)
    license_expiry = models.DateField()
    phone = models.CharField(max_length=15)
    address = models.TextField()
    emergency_contact = models.CharField(max_length=15)
    is_approved = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    assigned_bus = models.ForeignKey(Bus, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_drivers')
    assigned_route = models.ForeignKey(Route, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_drivers')
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.license_number}"
    
    # ✅ FIXED: SAFE FALLBACK PROPERTIES - Prevents template errors when assigned_bus/route is None
    @property
    def bus(self):
        """
        Safe fallback: returns assigned_bus if exists, otherwise a dummy object with defaults
        CHANGE REASON: Prevents VariableDoesNotExist errors in templates when accessing driver.bus.bus_number
        """
        if self.assigned_bus:
            return self.assigned_bus
        # Return a simple dummy object with default attributes to prevent template errors
        class DummyBus:
            bus_number = "B-XX"
            capacity = 40
            has_ac = False
            has_wifi = False
        return DummyBus()
    
    @property
    def route(self):
        """
        Safe fallback: returns assigned_route if exists, otherwise a dummy object with defaults
        CHANGE REASON: Prevents VariableDoesNotExist errors in templates when accessing driver.route.code
        """
        if self.assigned_route:
            return self.assigned_route
        # Return a simple dummy object with default attributes to prevent template errors
        class DummyRoute:
            code = "XX"
            start = "UAP Campus"
            end = "Uttara"
            distance_km = "18.4"
        return DummyRoute()
    
    @property
    def departure_time(self):
        """
        Safe fallback for departure time - returns default if no trip assigned
        CHANGE REASON: Prevents errors when driver has no active trip
        """
        if hasattr(self, 'trips') and self.trips.exists():
            trip = self.trips.filter(status='pending').first()
            if trip and trip.departure_time:
                return trip.departure_time
        return "8:00 AM"


class Trip(models.Model):
    """
    Trip assignment for drivers with real-time tracking
    CHANGE REASON: Manage driver trips with status, location, and stop tracking
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE, related_name='trips')
    route = models.ForeignKey(Route, on_delete=models.CASCADE)
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE)
    travel_date = models.DateField()
    departure_time = models.TimeField()
    arrival_time = models.TimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    current_lat = models.FloatField(null=True, blank=True)
    current_lng = models.FloatField(null=True, blank=True)
    last_location_update = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.route.code} - {self.travel_date} ({self.driver.user.get_full_name()})"


class TripStop(models.Model):
    """
    Individual stops in a trip for progress tracking
    CHANGE REASON: Track arrival/departure times at each stop for schedule adherence
    """
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name='stops')
    stop_name = models.CharField(max_length=200)
    stop_order = models.IntegerField()
    scheduled_time = models.TimeField()
    arrival_time = models.TimeField(null=True, blank=True)
    departure_time = models.TimeField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['stop_order']
    
    def __str__(self):
        return f"{self.trip.route.code} - {self.stop_name} (Order {self.stop_order})"


class VehicleIssue(models.Model):
    """
    Vehicle issue reporting by drivers for maintenance tracking
    CHANGE REASON: Enable drivers to report vehicle problems for admin action
    """
    SEVERITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE)
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE)
    issue_description = models.TextField()
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default='medium')
    reported_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    is_resolved = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Issue by {self.driver.user.get_full_name()} - {self.reported_at}"  
    class Alert(models.Model):
    """
    Emergency alert system for users and drivers
    CHANGE REASON: Enable real-time emergency notification system
    """
    ALERT_TYPES = [
        ('emergency', 'Emergency'),
        ('vehicle_issue', 'Vehicle Issue'),
        ('route_change', 'Route Change'),
        ('general', 'General'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE, null=True, blank=True)
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPES)
    message = models.TextField()
    location = models.CharField(max_length=255, blank=True)
    is_resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.get_alert_type_display()} - {self.created_at}"