from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


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

    def __str__(self):
        return self.name



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
    title = models.CharField(max_length=100)
    breakfast = models.TextField()
    lunch = models.TextField()
    dinner = models.TextField()
    calories = models.IntegerField()



class Payment(models.Model):
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
    DIFFICULTY_CHOICES = [
        ('Beginner', 'Beginner'),
        ('Intermediate', 'Intermediate'),
        ('Expert', 'Expert'),
    ]
    
    name = models.CharField(max_length=100)
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES)
    description = models.TextField()
    animation_url = models.URLField(help_text="Link to exercise GIF or Lottie animation")
    calories_per_rep = models.FloatField(default=0.5) # e.g., 0.5 kcal per pushup

    def __str__(self):
        return f"{self.name} ({self.difficulty})"
from django.db import models

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
    # Ensure this field exists for your intensity filtering
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='Beginner')
    muscle_group = models.CharField(max_length=50, choices=MUSCLE_CHOICES, default='Full Body')
    
    # Description for the exercises you mentioned (e.g., "Targets upper chest")
    description = models.TextField(blank=True, null=True)
    
    # URL or path for the exercise-specific GIF (e.g., a push-up animation)
    animation_url = models.URLField(max_length=500, blank=True, null=True)
    
    # For calorie calculation
    calories_per_rep = models.FloatField(default=0.1)

    def __str__(self):
        return f"{self.name} ({self.difficulty})"
