from django.shortcuts import render, redirect, get_object_or_404
from .models import Plan, Trainer, Member, Review, SuccessStory, Profile, GalleryMember, DietPlan, Payment
from frontend.models import Profile
from .forms import MemberForm, SignupForm, JoinForm, ContactForm, ReviewForm, ProfileForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import MemberUpdateForm
from django.http import StreamingHttpResponse
from .camera import PushUpDetector
from django.http import JsonResponse
from .models import HealthMemory
from .ai_engine import SmartCoach


# Home Page (use this as the main index view)
def home(request):
    plans = Plan.objects.all()
    trainers = Trainer.objects.all()
    reviews = Review.objects.select_related("user").order_by("-created_at")[:5]
    for review in reviews:
        review.member = getattr(review.user, "member", None)
    success_stories = SuccessStory.objects.order_by("-created_at")[:6]  # Fetch 6 latest stories
    print(f"Number of success stories fetched: {len(success_stories)}")  # Debug output
    print(f"Success stories titles: {[s.title for s in success_stories]}")  # Debug titles
    return render(request, "index.html", {"plans": plans, "trainers": trainers, "reviews": reviews, "success_stories": success_stories})

# Signup
def signup(request):
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            form.save()  # only creates the User
            return render(request, "signup_success.html")
        else:
           return render(request, "signup.html", {"form": form})
    else:
        form = SignupForm()
    return render(request, "signup.html", {"form": form})


# Join Now
def join_now(request):
    print("=== JOIN_NOW VIEW HIT ===")
    print(f"Request method: {request.method}")
    print(f"POST data: {request.POST}")
    print(f"FILES data: {request.FILES}")
    print(f"Available plans: {list(Plan.objects.all().values('title'))}")
    
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
        form.fields['plan'].queryset = Plan.objects.all()
    
    return render(request, 'join_now.html', {'form': form})

@login_required
def edit_profile(request):
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        # Basic Info
        profile.phone = request.POST.get('phone')
        profile.address = request.POST.get('address')
        profile.bio = request.POST.get('bio')
        profile.facebook = request.POST.get('facebook')
        profile.instagram = request.POST.get('instagram')
        profile.fitness_goal = request.POST.get('fitness_goal')

        # Numbers (Added default 0 or existing value to prevent crashes)
        profile.age = request.POST.get('age') or profile.age
        profile.weight = request.POST.get('weight') or profile.weight
        profile.height = request.POST.get('height') or profile.height
        
        profile.gender = request.POST.get('gender')

        # Date of Birth safety
        dob = request.POST.get('date_of_birth')
        if dob:
            profile.date_of_birth = dob

        # Profile Photo
        if request.FILES.get('photo'):
            profile.photo = request.FILES['photo']

        profile.save()
        
        # Syncing Email back to the main User model (Good practice)
        email = request.POST.get('email')
        if email:
            request.user.email = email
            request.user.save()

        return redirect('profile')

    return render(request, 'edit_profile.html', {'profile': profile})

@login_required
def profile(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    return render(request, 'profile.html', {'profile': profile})

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
    members = GalleryMember.objects.all()
    return render(request, "gallery.html", {"members": members})

def gallery_detail(request, id):
    member = get_object_or_404(GalleryMember, id=id)
    return render(request, "gallery_detail.html", {"member": member})

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
            return redirect("home")
    else:
        form = ReviewForm()
    return render(request, "add_review.html", {"form": form})

# Success Stories Page (optional separate view)
def success_stories(request):
    stories = SuccessStory.objects.all()
    return render(request, "success_stories.html", {"stories": stories})

# Detail View for Success Story
def success_detail(request, pk):
    story = get_object_or_404(SuccessStory, pk=pk)
    return render(request, "success_detail.html", {"story": story})

def diet(request):
    plans = DietPlan.objects.all() 
    return render(request, 'diet.html', {'plans': plans})

def payment(request):
    if request.method == "POST":
        amount = request.POST.get("amount")
        method = request.POST.get("method")
        trx_id = request.POST.get("trx_id")

        Payment.objects.create(
            amount=amount,
            method=method,
            transaction_id=trx_id,
            status="Pending"
        )

        return redirect("payment_success")

    return render(request, "payment.html")


def payment_success(request):
    return render(request, "payment_success.html")

def gen(camera):
    while True:
        frame = camera.get_frame()
        if frame:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

def video_feed(request):
    return StreamingHttpResponse(gen(PushUpDetector()),
                                 content_type='multipart/x-mixed-replace; boundary=frame')

# This function renders the HTML page
def workout_page(request):
    return render(request, 'workout.html')

@login_required
def chat_with_ai(request):
    if request.method == "POST":
        user_text = request.POST.get('text')
        
        # 1. ENSURE PROFILE EXISTS: This prevents the "User has no profile" error
        Profile.objects.get_or_create(user=request.user)
        
        # 2. SAVE TO MEMORY
        HealthMemory.objects.create(user=request.user, info_type="general", user_input=user_text)
        
        # 3. GET ADVICE
        coach = SmartCoach(request.user)
        response = coach.get_personalized_advice(user_text)
        
        return JsonResponse({'reply': response})