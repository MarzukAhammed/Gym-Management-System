from django import forms
from .models import Member,Plan
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Contact
from .models import Review

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
        fields = ["plan", "phone", "email", "address", "photo"]
        widgets = {
            "plan": forms.Select(attrs={"class": "form-control"}),  # Use Select for ForeignKey
            "phone": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter phone number"}),
            "email": forms.EmailInput(attrs={"class": "form-control", "placeholder": "Enter email"}),
            "address": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Enter your address"}),
            "photo": forms.ClearableFileInput(attrs={"class": "form-control"}),
        }

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