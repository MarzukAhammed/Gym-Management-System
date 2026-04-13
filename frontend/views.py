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
from .models import HealthMemory, MemberMemory, Exercise, UserProgress
from .ai_engine import SmartCoach
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
import json, datetime

# Home Page
def home(request):
    plans = Plan.objects.all()
    trainers = Trainer.objects.all()
    reviews = Review.objects.select_related("user").order_by("-created_at")[:5]
    for review in reviews:
        review.member = getattr(review.user, "member", None)
    success_stories = SuccessStory.objects.order_by("-created_at")[:6]
    return render(request, "index.html", {"plans": plans, "trainers": trainers, "reviews": reviews, "success_stories": success_stories})

# Signup
def signup(request):
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            form.save()
            return render(request, "signup_success.html")
        else:
            return render(request, "signup.html", {"form": form})
    else:
        form = SignupForm()
    return render(request, "signup.html", {"form": form})

# Join Now
def join_now(request):
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
        form = JoinForm()
        form.fields['plan'].queryset = Plan.objects.all()
    return render(request, 'join_now.html', {'form': form})

@login_required
def edit_profile(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        profile.phone = request.POST.get('phone')
        profile.address = request.POST.get('address')
        profile.bio = request.POST.get('bio')
        profile.facebook = request.POST.get('facebook')
        profile.instagram = request.POST.get('instagram')
        profile.fitness_goal = request.POST.get('fitness_goal')
        profile.age = request.POST.get('age') or profile.age
        profile.weight = request.POST.get('weight') or profile.weight
        profile.height = request.POST.get('height') or profile.height
        profile.gender = request.POST.get('gender')
        dob = request.POST.get('date_of_birth')
        if dob:
            profile.date_of_birth = dob
        if request.FILES.get('photo'):
            profile.photo = request.FILES['photo']
        profile.save()
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

# About, Plans, Team, Gallery
def about(request): return render(request, "about.html")
def plans_page(request): return render(request, "plans.html", {"plans": Plan.objects.all()})
def team(request): return render(request, "team.html", {"trainers": Trainer.objects.all()})
def gallery(request): return render(request, "gallery.html", {"members": GalleryMember.objects.all()})

def gallery_detail(request, id):
    member = get_object_or_404(GalleryMember, id=id)
    return render(request, "gallery_detail.html", {"member": member})

def testimonial(request):
    reviews = Review.objects.select_related("user").order_by("-created_at")
    for review in reviews:
        review.member = getattr(review.user, "member", None)
    return render(request, "testimonial.html", {"reviews": reviews})

def contact(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Message sent!")
            return redirect("contact")
    else:
        form = ContactForm()
    return render(request, "contact.html", {"form": form})

@login_required
def add_review(request):
    if request.method == "POST":
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.rating = review.rating or 5
            review.save()
            messages.success(request, "✅ Review added!")
            return redirect("home")
    return render(request, "add_review.html", {"form": ReviewForm()})

def success_stories(request): return render(request, "success_stories.html", {"stories": SuccessStory.objects.all()})
def success_detail(request, pk): return render(request, "success_detail.html", {"story": get_object_or_404(SuccessStory, pk=pk)})
def diet(request): return render(request, 'diet.html', {'plans': DietPlan.objects.all()})

def payment(request):
    if request.method == "POST":
        Payment.objects.create(
            amount=request.POST.get("amount"),
            method=request.POST.get("method"),
            transaction_id=request.POST.get("trx_id"),
            status="Pending"
        )
        return redirect("payment_success")
    return render(request, "payment.html")

def payment_success(request): return render(request, "payment_success.html")

# AI & Workout Logic
def gen(camera):
    while True:
        frame = camera.get_frame()
        if frame:
            yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

def video_feed(request):
    return StreamingHttpResponse(gen(PushUpDetector()), content_type='multipart/x-mixed-replace; boundary=frame')

def workout_page(request): return render(request, 'workout.html')

@ensure_csrf_cookie
def chat_with_ai(request):
    if request.method != 'POST': 
        return JsonResponse({'error': 'Post only'})
    
    user_msg = request.POST.get('text', '')
    coach = SmartCoach(request.user)
    
    # 1. Retrieve Memory & Identity
    if request.user.is_authenticated:
        mem, _ = MemberMemory.objects.get_or_create(user=request.user)
        username = request.user.username
    else:
        if not request.session.session_key: 
            request.session.create()
        mem, _ = MemberMemory.objects.get_or_create(session_key=request.session.session_key)
        username = "Guest"

    # 2. FIXED: History logic using sessions correctly
    raw_history = request.session.get('chat_history_list', [])
    history_text = " | ".join(raw_history[-3:]) if raw_history else "None"

    # 3. Call Groq
    response_data = coach.generate_response(user_msg, mem.ai_facts, history_text)

    try:
        # Clean AI response
        raw_content = response_data.strip()
        if raw_content.startswith("```json"):
            raw_content = raw_content.replace("```json", "", 1).replace("```", "", 1).strip()
        elif raw_content.startswith("```"):
            raw_content = raw_content.replace("```", "", 1).replace("```", "", 1).strip()

        ai_json = json.loads(raw_content)
        
        # Handle Internet Search
        if ai_json.get("search_query"):
            search_info = coach.search_internet(ai_json["search_query"])
            search_prompt = f"Internet results for '{ai_json['search_query']}': {search_info}. Answer: {user_msg}"
            response_data = coach.generate_response(search_prompt, mem.ai_facts, history_text)
            ai_json = json.loads(response_data.strip().replace("```json", "").replace("```", "").strip())

        # Update Facts
        if ai_json.get("new_facts"):
            mem.ai_facts.update(ai_json["new_facts"])
            mem.save()
        
        # FIXED: Update session history so she remembers next time
        history = request.session.get('chat_history_list', [])
        history.append(f"User: {user_msg}")
        history.append(f"Lolona: {ai_json.get('reply', '')}")
        request.session['chat_history_list'] = history[-10:] # Keep last 10 turns
        
        return JsonResponse({'reply': ai_json.get('reply', "Meow!")})

    except Exception as e:
        print(f"Error: {e}")
        return JsonResponse({'reply': response_data if response_data else "I'm still learning! Try again."})


@login_required
def track_workout(request):
    if request.method == "POST":
        exercise_id = request.POST.get('exercise_id')
        reps = int(request.POST.get('reps', 0))
        
        exercise = get_object_or_404(Exercise, id=exercise_id)
        calories_burned = reps * exercise.calories_per_rep
        
        # Get user profile to update calorie goal
        profile = request.user.profile
        profile.daily_calorie_goal -= calories_burned
        profile.save()
        
        messages.success(request, f"🔥 Burned {calories_burned} kcal! Remaining goal: {profile.daily_calorie_goal} kcal.")
        return redirect('exercise_library')

    exercises = Exercise.objects.all()
    return render(request, 'exercise_library.html', {'exercises': exercises})

def training_session(request):
    return render(request, 'training.html')


@login_required
def progress_dashboard(request):
    # 1. Get user profile info
    user_profile = getattr(request.user, 'profile', None) 
    
    # 2. Get the 7 most recent entries (ordered by date descending, then reversed for the chart)
    # This ensures you see the latest progress from left to right
    logs = UserProgress.objects.filter(user=request.user).order_by('-date')[:7]
    logs = reversed(logs) # Flip them so the oldest of the 7 is on the left
    
    dates = []
    calories = []
    durations = []

    for log in logs:
        dates.append(log.date.strftime("%b %d"))
        calories.append(float(log.calories_burned))
        durations.append(float(log.workout_duration))

    # 3. Build the context (Indented exactly 4 spaces)
    context = {
        'user_full_name': request.user.get_full_name() or request.user.username,
        'current_weight': getattr(user_profile, 'weight', 0),
        'goal_weight': getattr(user_profile, 'goal_weight', 0),
        'user_height': getattr(user_profile, 'height', 0),
        'total_calories': sum(calories),
        'dates_json': json.dumps(dates),
        'calories_json': json.dumps(calories),
        'durations_json': json.dumps(durations),
    }

    # 4. Return the response (Indented exactly 4 spaces)
    return render(request, 'progress.html', context)
    
@login_required
def update_stats(request):
    """Handles the form submission from the progress dashboard."""
    if request.method == "POST":
        new_weight = request.POST.get('weight')
        
        # 1. Update the User's Profile weight
        # Assumes request.user has a related 'profile' model
        if hasattr(request.user, 'profile'):
            profile = request.user.profile
            profile.weight = new_weight
            profile.save()

        # 2. Update or Create a log for today in UserProgress
        # This is what moves the line on your Chart.js graph
        UserProgress.objects.update_or_create(
            user=request.user, 
            date=datetime.date.today(),
            defaults={'current_weight': new_weight}
        )
        
        # Redirect back to the progress page to see the update
        return redirect('progress_tracker')

def record_workout_data(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        exercise_name = data.get('exercise_name')
        duration_mins = float(data.get('duration', 0))
        
        # 1. Calculate Burn
        try:
            exercise = Exercise.objects.get(name=exercise_name)
            calories_burned = exercise.calories_per_minute * duration_mins
        except Exercise.DoesNotExist:
            calories_burned = 5 * duration_mins # Default fallback

        # 2. Update Progress Table
        progress, created = UserProgress.objects.get_or_create(
            user=request.user,
            date=datetime.date.today()
        )
        
        progress.calories_burned += int(calories_burned)
        progress.workout_duration += int(duration_mins)
        progress.save()

        return JsonResponse({'status': 'success', 'burned': calories_burned})

@csrf_exempt
def save_diet_plan_from_ai(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            DietPlan.objects.create(
                title=data.get('title', 'AI Plan'),
                calories=data.get('calories', 2000),
                breakfast=data.get('breakfast', 'Healthy meal'),
                lunch=data.get('lunch', 'Healthy meal'),
                dinner=data.get('dinner', 'Healthy meal')
            )
            return JsonResponse({'status': 'success', 'message': 'Plan saved!'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

@csrf_exempt
def delete_diet_plan_ai(request):
    if request.method == 'POST':
        from .models import DietPlan
        DietPlan.objects.all().delete() # Eita shob delete korbe
        return JsonResponse({'status': 'success'})