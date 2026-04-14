from django import forms
from .models import Member, Plan, Profile, SuccessStory, Trainer
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Contact
from .models import Review


class TrainerCreateForm(forms.ModelForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={"class": "form-control"}))
    password1 = forms.CharField(required=True, widget=forms.PasswordInput(attrs={"class": "form-control"}))
    password2 = forms.CharField(required=True, widget=forms.PasswordInput(attrs={"class": "form-control"}))

    class Meta:
        model = Trainer
        fields = ["name", "specialty", "bio", "photo", "facebook", "twitter", "linkedin"]

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get("password1")
        p2 = cleaned.get("password2")
        if p1 and p2 and p1 != p2:
            self.add_error("password2", "Passwords do not match.")
        return cleaned

    def save(self, commit=True):
        trainer = super().save(commit=False)
        email = self.cleaned_data["email"]
        password = self.cleaned_data["password1"]

        username = email.split("@")[0]
        base = username
        i = 1
        while User.objects.filter(username=username).exists():
            i += 1
            username = f"{base}{i}"

        user = User.objects.create_user(username=username, email=email, password=password)
        trainer.user = user

        if commit:
            trainer.save()
        return trainer

# For creating/updating member profile
class MemberForm(forms.ModelForm):
    class Meta:
        model = Member
        fields = ["name", "email", "phone", "address", "photo", "plan"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Full Name"}),
            "email": forms.EmailInput(attrs={"class": "form-control", "placeholder": "Email"}),
            "phone": forms.TextInput(attrs={"class": "form-control", "placeholder": "Phone Number"}),
            "address": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Address"}),
            "photo": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "plan": forms.Select(attrs={"class": "form-control"}),  # For ForeignKey to Plan
        }

# For user signup
class SignupForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control", "placeholder": "Username"}),
            "email": forms.EmailInput(attrs={"class": "form-control", "placeholder": "Email"}),
            "password1": forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Password"}),
            "password2": forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Confirm Password"}),
        }

# For Join Now form
class JoinForm(forms.ModelForm):
    plan = forms.ModelChoiceField(queryset=Plan.objects.all(), empty_label="Select a Plan")
    class Meta:
        model = Member
        fields = ["plan", "phone", "email", "address"]
        widgets = {
            "plan": forms.Select(attrs={"class": "form-control"}),  # Use Select for ForeignKey
            "phone": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter phone number"}),
            "email": forms.EmailInput(attrs={"class": "form-control", "placeholder": "Enter email"}),
            "address": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Enter your address"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["plan"].label_from_instance = self._plan_label

    @staticmethod
    def _plan_label(plan):
        title = (getattr(plan, "title", "") or "").strip().lower()
        if "basic" in title or "starter" in title:
            return "Starter (Basic)"
        if "standard" in title or "pro" in title:
            return "Pro (Standard)"
        if "premium" in title or "elite" in title:
            return "Elite (Premium)"
        # Fallback for any other plan title
        return f"{plan.title} ({plan.duration})"

class MemberUpdateForm(forms.ModelForm):
    class Meta:
        model = Member
        fields = [
            "phone", "address", "photo", "bio",
            "age", "gender", "date_of_birth",
            "facebook", "instagram"
        ]

class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ["name", "email", "message"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Your Name"}),
            "email": forms.EmailInput(attrs={"class": "form-control", "placeholder": "Your Email"}),
            "message": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Your Message"}),
        }

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ["rating", "comment"]
        widgets = {
            "rating": forms.NumberInput(attrs={"min": 1, "max": 5, "class": "form-control"}),
            "comment": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Write your feedback..."}),
        }

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        # Explicitly listing fields ensures they are processed in order
        fields = [
            'photo', 'bio', 'phone', 'address', 
            'weight', 'height', 'age', 'gender', 'fitness_goal',
            'date_of_birth', 'facebook', 'instagram'
        ]
        widgets = {
            'weight': forms.NumberInput(attrs={'class': 'custom-input', 'step': '0.1'}),
            'height': forms.NumberInput(attrs={'class': 'custom-input', 'step': '0.1'}),
            'age': forms.NumberInput(attrs={'class': 'custom-input'}),
            'gender': forms.Select(attrs={'class': 'custom-select'}),
            'fitness_goal': forms.TextInput(attrs={'class': 'custom-input'}),
            'bio': forms.Textarea(attrs={'class': 'custom-input', 'rows': 3}),
            'address': forms.Textarea(attrs={'class': 'custom-input', 'rows': 2}),
            'date_of_birth': forms.DateInput(attrs={'class': 'custom-input', 'type': 'date'}),
        }


class SuccessStoryForm(forms.ModelForm):
    class Meta:
        model = SuccessStory
        fields = ["title", "story", "photo"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control", "placeholder": "Story title"}),
            "story": forms.Textarea(attrs={"class": "form-control", "rows": 6, "placeholder": "Share your transformation journey..."}),
            "photo": forms.ClearableFileInput(attrs={"class": "form-control"}),
        }