from django.shortcuts import render, redirect
from .models import Plan, Trainer, Member, Review
from .forms import MemberForm, SignupForm, JoinForm, ContactForm, ReviewForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages

# Home Page
def home(request):
    plans = Plan.objects.all()
    trainers = Trainer.objects.all()
    reviews = Review.objects.select_related("user").order_by("-created_at")[:5]
    for review in reviews:
        review.member = getattr(review.user, "member", None)
    return render(request, "index.html", {"plans": plans, "trainers": trainers, "reviews": reviews})

# Signup
def signup(request):
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "You are registered successfully! Please login.")
            return redirect("login")
    else:
        form = SignupForm()
    return render(request, "signup.html", {"form": form})

# Join Now
def join_now(request):
    print("=== JOIN_NOW VIEW HIT ===")
    print(f"Request method: {request.method}")
    print(f"POST data: {request.POST}")
    print(f"FILES data: {request.FILES}")
    print(f"Available plans: {list(Plan.objects.all().values('title'))}")  # Debug plan data
    
    if request.method == 'POST':
        form = JoinForm(request.POST, request.FILES)
        if form.is_valid():
            email = form.cleaned_data['email']
            if Member.objects.filter(email=email).exists():
                messages.error(request, "A member with this email already exists.")
            else:
                member = form.save(commit=False)
                if request.user.is_authenticated:
                    member.user = request.user
                member.save()
                messages.success(request, "🎉 You have successfully joined our gym!")
                return redirect('home')
        else:
            print(f"Form errors: {form.errors}")
            messages.error(request, "Please correct the errors in the form.")
    else:
        form = JoinForm()
        form.fields['plan'].queryset = Plan.objects.all()  # Set queryset here
    
    return render(request, 'join_now.html', {'form': form})

# Profile
@login_required
def profile(request):
    member = getattr(request.user, "member", None)
    return render(request, "profile.html", {"member": member})

# About Page
def about(request):
    return render(request, "about.html")

# Plans Page
def plans_page(request):
    plans = Plan.objects.all()
    return render(request, "plans.html", {"plans": plans})

# Team Page
def team(request):
    trainers = Trainer.objects.all()
    return render(request, "team.html", {"trainers": trainers})

# Gallery
def gallery(request):
    return render(request, "gallery.html")

# Testimonials
def testimonial(request):
    reviews = Review.objects.select_related("user").order_by("-created_at")
    for review in reviews:
        review.member = getattr(review.user, "member", None)
    return render(request, "testimonial.html", {"reviews": reviews})

# Contact
def contact(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Your message has been sent! We’ll get back to you soon.")
            return redirect("contact")
    else:
        form = ContactForm()
    return render(request, "contact.html", {"form": form})

# Index
def index(request):
    reviews = Review.objects.select_related("user").order_by("-created_at")
    return render(request, "index.html", {"reviews": reviews})

# Add Review
@login_required
def add_review(request):
    if request.method == "POST":
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            if not review.rating:  # Ensure rating is not None
                review.rating = 5
            review.save()
            messages.success(request, "✅ Your review has been added successfully!")
            return redirect("home")  # Change from "index" to "home"
    else:
        form = ReviewForm()
    return render(request, "add_review.html", {"form": form})