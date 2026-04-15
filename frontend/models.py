from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import uuid


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

class Plan(models.Model):
    title = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    duration = models.CharField(max_length=50)   # e.g. "Month", "Month/3", "1 Month"
    description = models.TextField(blank=True)    # can contain multiple lines; linebreaks will render <p> tags
    image = models.ImageField(upload_to='plans/', blank=True, null=True)

    def BDT (self):
        return self.title





class Trainer(models.Model):
    name = models.CharField(max_length=100)
    specialty = models.CharField(max_length=100)
    bio = models.TextField(blank=True)
    photo = models.ImageField(upload_to='trainers/', blank=True, null=True)
    facebook = models.URLField(blank=True, null=True)
    twitter = models.URLField(blank=True, null=True)
    linkedin = models.URLField(blank=True, null=True)
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="trainer_account")

    def __str__(self):
        return self.name


class TrainingSlot(models.Model):
    trainer = models.ForeignKey(Trainer, on_delete=models.CASCADE, related_name="training_slots")
    session_time = models.DateTimeField()
    is_active = models.BooleanField(default=False)  # trainer controls when the room is open
    meeting_link = models.URLField(max_length=500)
    is_booked = models.BooleanField(default=False)
    booked_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="booked_training_slots")

    class Meta:
        ordering = ["session_time"]

    def __str__(self):
        return f"{self.trainer.name} slot @ {self.session_time}"

    @staticmethod
    def generate_meeting_link():
        room = f"mpower-{uuid.uuid4().hex[:12]}"
        return f"https://meet.jit.si/{room}"


class TrainingSession(models.Model):
    trainer = models.ForeignKey(Trainer, on_delete=models.CASCADE, related_name="training_sessions")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="training_sessions")
    session_time = models.DateTimeField()
    is_active = models.BooleanField(default=False)
    meeting_link = models.URLField(max_length=500)

    def __str__(self):
        return f"{self.trainer.name} with {self.user.username} @ {self.session_time}"

    @staticmethod
    def generate_meeting_link():
        room = f"gymnasium-{uuid.uuid4().hex[:12]}"
        return f"https://meet.jit.si/{room}"


class Notification(models.Model):
    LEVEL_CHOICES = [
        ("success", "Success"),
        ("info", "Info"),
        ("warning", "Warning"),
        ("error", "Error"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    level = models.CharField(max_length=10, choices=LEVEL_CHOICES, default="info")
    text = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} - {self.level}"


class DailyChallenge(models.Model):
    DAY_CHOICES = [
        (0, "Monday"),
        (1, "Tuesday"),
        (2, "Wednesday"),
        (3, "Thursday"),
        (4, "Friday"),
        (5, "Saturday"),
        (6, "Sunday"),
    ]

    title = models.CharField(max_length=120)
    instruction = models.CharField(max_length=255, blank=True, default="")
    day_of_week = models.IntegerField(choices=DAY_CHOICES)
    coins_reward = models.PositiveIntegerField(default=10)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.title} ({self.get_day_of_week_display()})"


class ChallengeSubmission(models.Model):
    challenge = models.ForeignKey(DailyChallenge, on_delete=models.CASCADE, related_name="submissions")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="challenge_submissions")
    proof_video = models.FileField(upload_to="challenge_proofs/")
    created_at = models.DateTimeField(auto_now_add=True)
    coins_granted = models.PositiveIntegerField(default=0)
    coins_approved = models.BooleanField(default=False)
    coins_approved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} - {self.challenge.title}"


class ChallengeVideoComment(models.Model):
    submission = models.ForeignKey(ChallengeSubmission, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="challenge_video_comments")
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.user.username} on #{self.submission_id}"


class UserChallengeProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="challenge_profile")
    current_streak = models.PositiveIntegerField(default=0)
    last_completed_date = models.DateField(null=True, blank=True)
    gym_coins = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.user.username} streak={self.current_streak} coins={self.gym_coins}"



class Member(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)   # ✅ keep only one address
    photo = models.ImageField(upload_to='members/', blank=True, null=True)
    join_date = models.DateTimeField(auto_now_add=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    plan = models.CharField(max_length=100, default="Basic")
    bio = models.TextField(blank=True, null=True)
    age = models.IntegerField(blank=True, null=True)
    gender = models.CharField(max_length=10, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    facebook = models.URLField(blank=True, null=True)
    instagram = models.URLField(blank=True, null=True)


    def __str__(self):
        if self.user:
            return self.user.username
        return "Unlinked Member"
    
class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.email}"

class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(default=0)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.rating} stars"


class TrainerReview(models.Model):
    trainer = models.ForeignKey(Trainer, on_delete=models.CASCADE, related_name="reviews")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="trainer_reviews")
    rating = models.PositiveIntegerField(default=5)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        unique_together = ("trainer", "user")

    def __str__(self):
        return f"{self.trainer.name} - {self.user.username} ({self.rating}★)"
    
class SuccessStory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="success_stories")
    title = models.CharField(max_length=200)
    story = models.TextField()
    photo = models.ImageField(upload_to="success_stories/", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    photo = models.ImageField(upload_to="profile_photos/", blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    goal_weight = models.DecimalField(max_digits=5, decimal_places=2, default=70.0)
    gym_coins = models.PositiveIntegerField(default=0)
    height = models.DecimalField(max_digits=5, decimal_places=2, default=170.0) # in cm
    
    # --- ADD THESE THREE FIELDS ---
    weight = models.FloatField(default=0.0) 
    height = models.FloatField(default=0.0)
    fitness_goal = models.CharField(max_length=255, blank=True, null=True)
    # ------------------------------

    age = models.IntegerField(null=True, blank=True)
    gender = models.CharField(max_length=20, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    facebook = models.CharField(max_length=255, blank=True, null=True)
    instagram = models.CharField(max_length=255, blank=True, null=True)

    # ADD THIS FUNCTION FOR THE CALORIE CALCULATION
    def calculate_daily_calories(self):
        """Calculates BMR - calories burned at rest."""
        if not self.weight or not self.height or not self.age:
            return 0
        
        # Mifflin-St Jeor Equation
        if self.gender and self.gender.lower() == 'male':
            bmr = (10 * self.weight) + (6.25 * self.height) - (5 * self.age) + 5
        else:
            bmr = (10 * self.weight) + (6.25 * self.height) - (5 * self.age) - 161
        return round(bmr)

    def __str__(self):
        return self.user.username
    

class GalleryMember(models.Model):
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=100, blank=True, null=True)   # Example: Fitness Trainer
    joined_year = models.CharField(max_length=10, blank=True, null=True)
    specialty = models.CharField(max_length=200, blank=True, null=True)
    program = models.CharField(max_length=200, blank=True, null=True)
    experience = models.CharField(max_length=50, blank=True, null=True)
    image = models.ImageField(upload_to="gallery/")

    def __str__(self):
        return self.name


class DietPlan(models.Model):
    title = models.CharField(max_length=255)
    calories = models.IntegerField()
    breakfast = models.TextField(default="Healthy Breakfast") # Eita add korun
    lunch = models.TextField(default="Healthy Lunch")         # Eita add korun
    dinner = models.TextField(default="Healthy Dinner")       # Eita add korun

    def __str__(self):
        return self.title



class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="payments", null=True, blank=True)
    full_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    amount = models.IntegerField()
    method = models.CharField(
        max_length=20,
        choices=[
            ('bkash', 'bKash'),
            ('nagad', 'Nagad')
        ]
    )
    transaction_id = models.CharField(
    max_length=100,
    blank=True,
    default=''
)
    verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} - {self.amount} BDT"

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    weight = models.FloatField() # in kg
    height = models.FloatField() # in cm
    age = models.IntegerField()
    gender = models.CharField(max_length=10, choices=[('male', 'Male'), ('female', 'Female')])
    fitness_goal = models.CharField(max_length=255)

    def calculate_daily_calories(self):
        """Calculates BMR - calories burned at rest."""
        if self.gender == 'male':
            bmr = (10 * self.weight) + (6.25 * self.height) - (5 * self.age) + 5
        else:
            bmr = (10 * self.weight) + (6.25 * self.height) - (5 * self.age) - 161
        return round(bmr)

    def __str__(self):
        return f"{self.user.username}'s Profile"
class HealthMemory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE) # Must be on_delete here too
    info_type = models.CharField(max_length=50)
    user_input = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.info_type}"

class MemberMemory(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    session_key = models.CharField(max_length=40, null=True, blank=True, unique=True)
    ai_facts = models.JSONField(default=dict, blank=True) # Stores location, goals, etc.

    def __str__(self):
        return f"Memory for {self.user.username if self.user else self.session_key}"

class Exercise(models.Model):
    MUSCLE_CHOICES = [
        ('Chest', 'Chest'),
        ('Back', 'Back'),
        ('Legs', 'Legs'),
        ('Arms', 'Arms'),
        ('Core', 'Core'),
        ('Full Body', 'Full Body'),
    ]

    DIFFICULTY_CHOICES = [
        ('Beginner', 'Beginner'),
        ('Intermediate', 'Intermediate'),
        ('Expert', 'Expert'),
    ]

    name = models.CharField(max_length=100)
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='Beginner')
    muscle_group = models.CharField(max_length=50, choices=MUSCLE_CHOICES, default='Full Body')
    description = models.TextField(blank=True, null=True)
    animation_url = models.URLField(max_length=500, blank=True, null=True, help_text="Link to exercise GIF or animation")
    calories_per_minute = models.IntegerField(default=5)
    calories_per_rep = models.FloatField(default=0.1)

    def __str__(self):
        return f"{self.name} ({self.difficulty})"


class UserProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='progress_logs')
    date = models.DateField(auto_now_add=True)
    calories_burned = models.IntegerField(default=0, help_text="Total calories burned today")
    workout_duration = models.IntegerField(default=0, help_text="Duration in minutes")
    current_weight = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    class Meta:
        ordering = ['-date'] # Newest first
        # Ensure only one log per user per day
        unique_together = ('user', 'date')

    def __str__(self):
        return f"{self.user.username} - {self.date}"
