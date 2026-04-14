from django.shortcuts import render, redirect, get_object_or_404
from .models import Plan, Trainer, Member, Review, SuccessStory, Profile, GalleryMember, DietPlan, Payment, TrainingSession, Notification, TrainingSlot
from frontend.models import Profile
from .forms import MemberForm, SignupForm, JoinForm, ContactForm, ReviewForm, ProfileForm, SuccessStoryForm
from django.contrib.auth import login
from django.contrib.auth.models import User
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
import re
from pathlib import Path
from functools import lru_cache
from django.conf import settings
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.contrib.admin.views.decorators import staff_member_required

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
                selected_plan = form.cleaned_data.get('plan')
                if selected_plan:
                    member.plan = selected_plan.title
                if request.user.is_authenticated:
                    member.user = request.user
                member.save()
                messages.success(request, "🎉 You have successfully joined our gym!")
                return redirect('payment')
    else:
        form = JoinForm()
        form.fields['plan'].queryset = Plan.objects.all()
    return render(request, 'join_now.html', {'form': form})

@login_required
def edit_profile(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        full_name = (request.POST.get('name') or '').strip()
        if full_name:
            name_parts = full_name.split()
            request.user.first_name = name_parts[0]
            request.user.last_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""

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
    member = getattr(request.user, 'member', None)
    payment_qs = Payment.objects.filter(verified=True, full_name__iexact=request.user.username)
    user_phone = ""
    if member and getattr(member, "phone", None):
        user_phone = member.phone
    elif profile and getattr(profile, "phone", None):
        user_phone = profile.phone

    if user_phone:
        verified_payment = payment_qs.filter(phone=user_phone).exists()
    else:
        verified_payment = payment_qs.exists()

    def _resolve_plan_name(raw_plan_value):
        if not raw_plan_value:
            return None
        raw = str(raw_plan_value).strip()
        match = re.search(r"Plan object \((\d+)\)", raw)
        if match:
            try:
                plan_obj = Plan.objects.filter(id=int(match.group(1))).first()
                if plan_obj:
                    return plan_obj.title
            except Exception:
                pass
        return raw

    def _friendly_plan_name(raw_name):
        if not raw_name:
            return raw_name
        n = raw_name.strip().lower()
        if "basic" in n or "starter" in n:
            return "Starter (Basic)"
        if "standard" in n or "pro" in n:
            return "Pro (Standard)"
        if "premium" in n or "elite" in n:
            return "Elite (Premium)"
        return raw_name

    clean_plan_name = _resolve_plan_name(member.plan) if member else None
    display_plan_name = _friendly_plan_name(clean_plan_name) if clean_plan_name else None
    selected_plan = display_plan_name if display_plan_name and verified_payment else None
    pending_plan = display_plan_name if display_plan_name and not verified_payment else None
    return render(request, 'profile.html', {
        'profile': profile,
        'selected_plan': selected_plan,
        'pending_plan': pending_plan,
    })

# About, Plans, Team, Gallery
def about(request): return render(request, "about.html")
def plans_page(request): return render(request, "plans.html", {"plans": Plan.objects.all()})
def team(request): return render(request, "team.html", {"trainers": Trainer.objects.all()})
def gallery(request): return render(request, "gallery.html", {"members": GalleryMember.objects.all()})
def privacy_policy(request): return render(request, "privacy_policy.html")
def terms_conditions(request): return render(request, "terms_conditions.html")
def refund_policy(request): return render(request, "refund_policy.html")

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


@login_required
def add_success_story(request):
    if request.method == "POST":
        form = SuccessStoryForm(request.POST, request.FILES)
        if form.is_valid():
            story = form.save(commit=False)
            story.user = request.user
            story.save()
            messages.success(request, "✅ Your success story has been published.")
            return redirect("profile")
    else:
        form = SuccessStoryForm()
    return render(request, "add_success_story.html", {"form": form})


def _extract_calories_from_text(text):
    if not text:
        return None
    match = re.search(r"(\d{2,5})\s*(kcal|calories?)", str(text), flags=re.IGNORECASE)
    return int(match.group(1)) if match else None


def _compute_total_plan_calories(breakfast, lunch, dinner, fallback=2000):
    values = [
        _extract_calories_from_text(breakfast),
        _extract_calories_from_text(lunch),
        _extract_calories_from_text(dinner),
    ]
    numbers = [v for v in values if isinstance(v, int)]
    return sum(numbers) if numbers else int(fallback or 2000)


def diet(request):
    plans = DietPlan.objects.all()
    for plan in plans:
        # Always show computed calories from meal lines when available.
        plan.display_calories = _compute_total_plan_calories(
            plan.breakfast,
            plan.lunch,
            plan.dinner,
            fallback=plan.calories
        )
    return render(request, 'diet.html', {'plans': plans})

def payment(request):
    if request.method == "POST":
        amount = request.POST.get("amount")
        sender_number = request.POST.get("sender_number")
        reference_username = request.POST.get("reference_username")
        trx_id = request.POST.get("trx_id")

        if not amount or not sender_number or not reference_username:
            messages.error(request, "Please fill all required payment details.")
            return redirect("payment")

        # Use authenticated username as authoritative payment owner.
        if request.user.is_authenticated:
            reference_username = request.user.username

        Payment.objects.create(
            full_name=reference_username,
            phone=sender_number,
            amount=amount,
            method="bkash",
            transaction_id=trx_id or f"REF-{reference_username}-{sender_number}"
        )
        return redirect("payment_success")

    default_username = request.user.username if request.user.is_authenticated else ""
    return render(request, "payment.html", {"default_username": default_username})

def payment_success(request): return render(request, "payment_success.html")


@login_required
def mark_notification_read(request):
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "POST only"}, status=405)
    try:
        data = json.loads(request.body or "{}")
        notif_id = str(data.get("notification_id", "")).strip()
        if not notif_id:
            return JsonResponse({"status": "error", "message": "notification_id required"}, status=400)
        Notification.objects.filter(id=notif_id, user=request.user).update(is_read=True)
        return JsonResponse({"status": "success"})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=400)


@login_required
def clear_notification(request):
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "POST only"}, status=405)
    try:
        data = json.loads(request.body or "{}")
        notif_id = str(data.get("notification_id", "")).strip()
        if not notif_id:
            return JsonResponse({"status": "error", "message": "notification_id required"}, status=400)
        Notification.objects.filter(id=notif_id, user=request.user).delete()
        return JsonResponse({"status": "success"})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=400)


@login_required
def notification_history(request):
    items = Notification.objects.filter(user=request.user).order_by("-created_at")[:200]
    # Mark all as read when visiting history (simple UX).
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return render(request, "notification_history.html", {"items": items})

# AI & Workout Logic
def gen(camera):
    while True:
        frame = camera.get_frame()
        if frame:
            yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

def video_feed(request):
    return StreamingHttpResponse(gen(PushUpDetector()), content_type='multipart/x-mixed-replace; boundary=frame')

def workout_page(request): return render(request, 'workout.html')


def _clean_template_text(html_text):
    text = re.sub(r"<script[\s\S]*?</script>", " ", html_text, flags=re.IGNORECASE)
    text = re.sub(r"<style[\s\S]*?</style>", " ", text, flags=re.IGNORECASE)
    text = re.sub(r"{%[\s\S]*?%}", " ", text)
    text = re.sub(r"{{[\s\S]*?}}", " ", text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


@lru_cache(maxsize=1)
def _get_template_knowledge_chunks():
    templates_dir = Path(settings.BASE_DIR) / "templates"
    if not templates_dir.exists():
        return []

    chunks = []
    for html_file in templates_dir.rglob("*.html"):
        try:
            raw = html_file.read_text(encoding="utf-8", errors="ignore")
            cleaned = _clean_template_text(raw)
            if not cleaned:
                continue
            chunks.append({
                "page": str(html_file.relative_to(templates_dir)).replace("\\", "/"),
                "text": cleaned[:1400]
            })
        except Exception:
            continue
    return chunks


def _build_relevant_site_context(user_query, limit=4):
    chunks = _get_template_knowledge_chunks()
    if not chunks:
        return "No local page knowledge available."

    terms = {t for t in re.findall(r"[a-zA-Z]{3,}", user_query.lower())}
    scored = []
    for c in chunks:
        body_lower = c["text"].lower()
        score = sum(1 for t in terms if t in body_lower)
        if score > 0:
            scored.append((score, c))

    scored.sort(key=lambda x: x[0], reverse=True)
    chosen = [item[1] for item in scored[:limit]]
    if not chosen:
        chosen = chunks[:2]

    context_lines = [
        f"[{c['page']}] {c['text'][:500]}"
        for c in chosen
    ]
    return "\n".join(context_lines)


def _build_profile_context(request):
    """Builds DB-backed profile context so AI can access full user profile data."""
    if not request.user.is_authenticated:
        return "Guest user (no profile context)."

    profile = getattr(request.user, "profile", None)
    member = getattr(request.user, "member", None)

    if not profile and not member:
        return f"Username: {request.user.username}. No profile/member record found."

    context_parts = [f"Username: {request.user.username}"]
    if request.user.email:
        context_parts.append(f"Email: {request.user.email}")

    if profile:
        context_parts.extend([
            f"Age: {getattr(profile, 'age', '')}",
            f"Gender: {getattr(profile, 'gender', '')}",
            f"Weight: {getattr(profile, 'weight', '')}",
            f"Height: {getattr(profile, 'height', '')}",
            f"Goal Weight: {getattr(profile, 'goal_weight', '')}",
            f"Fitness Goal: {getattr(profile, 'fitness_goal', '')}",
            f"Phone: {getattr(profile, 'phone', '')}",
            f"Address: {getattr(profile, 'address', '')}",
            f"Bio: {getattr(profile, 'bio', '')}",
            f"Date of Birth: {getattr(profile, 'date_of_birth', '')}",
            f"Facebook: {getattr(profile, 'facebook', '')}",
            f"Instagram: {getattr(profile, 'instagram', '')}",
        ])

    if member:
        context_parts.extend([
            f"Member Plan: {getattr(member, 'plan', '')}",
            f"Member Phone: {getattr(member, 'phone', '')}",
            f"Member Address: {getattr(member, 'address', '')}",
        ])

    # Remove empty values to keep prompt compact.
    cleaned = [part for part in context_parts if not part.endswith(": ") and not part.endswith(":")]
    return " | ".join(cleaned)


def _profile_usage_summary(request):
    """Short profile summary for transparent AI replies."""
    if not request.user.is_authenticated:
        return ""
    profile = getattr(request.user, "profile", None)
    if not profile:
        return ""

    used = []
    if getattr(profile, "weight", None):
        used.append(f"weight {profile.weight}")
    if getattr(profile, "height", None):
        used.append(f"height {profile.height}")
    if getattr(profile, "age", None):
        used.append(f"age {profile.age}")
    if getattr(profile, "fitness_goal", None):
        used.append(f"goal {profile.fitness_goal}")

    return ", ".join(used[:4])


def _is_profile_related_query(text):
    query = (text or "").lower()
    explicit_self_phrases = [
        "my profile",
        "my data",
        "my details",
        "use my profile",
        "based on my profile",
        "using my data",
        "my weight",
        "my height",
        "my age",
        "my goal",
        "my bmi",
    ]
    return any(p in query for p in explicit_self_phrases)

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
    site_context = _build_relevant_site_context(user_msg)
    profile_context = _build_profile_context(request)
    persona = (
        "You are Lolona AI — a grumpy, witty cat fitness assistant for M-Power Fitness Lab. "
        "Stay in character. Keep replies helpful and concise. "
        "Use light sarcasm, never rude or hateful. No robotic/automated tone. "
        "If the user is not logged in, you can tease them about it."
    )
    enriched_input = f"{persona}\n\nUser: {user_msg}\n\nUser Profile Context: {profile_context}"

    # 3. Call Groq
    response_data = coach.generate_response(enriched_input, mem.ai_facts, history_text, site_context)

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
            search_prompt = f"Internet results for '{ai_json['search_query']}': {search_info}. Answer: {enriched_input}"
            response_data = coach.generate_response(search_prompt, mem.ai_facts, history_text, site_context)
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
        
        reply_text = ai_json.get('reply', "Meow!")
        if _is_profile_related_query(user_msg):
            summary = _profile_usage_summary(request)
            if summary:
                reply_text = f"Using your profile data ({summary}). {reply_text}"

        return JsonResponse({'reply': reply_text})

    except Exception as e:
        print(f"Error: {e}")
        return JsonResponse({'reply': response_data if response_data else "I'm still learning! Try again."})


@login_required
def track_workout(request):
    beginner_back_exercises = [
        {
            "name": "Superman Hold",
            "muscle_group": "Back",
            "difficulty": "Beginner",
            "description": "Lie prone and lift arms/legs together to activate lower back.",
            "animation_url": "/static/videos/exercises/superman_hold.mp4",
            "calories_per_rep": 0.3,
        },
        {
            "name": "Bird-Dog",
            "muscle_group": "Back",
            "difficulty": "Beginner",
            "description": "Core and back stability drill with opposite arm-leg extension.",
            "animation_url": "/static/videos/exercises/bird_dog.mp4",
            "calories_per_rep": 0.25,
        },
        {
            "name": "Reverse Snow Angel",
            "muscle_group": "Back",
            "difficulty": "Beginner",
            "description": "Great for upper-back posture and shoulder control.",
            "animation_url": "/static/videos/exercises/reverse_snow_angel.mp4",
            "calories_per_rep": 0.28,
        },
    ]

    for item in beginner_back_exercises:
        Exercise.objects.get_or_create(name=item["name"], defaults=item)

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

    hidden_seed_exercises = [
        "Push-Up",
        "Bodyweight Squat",
        "Plank Hold",
        "Seated Cable Row (Light)",
        "Lat Pulldown (Wide Grip)",
        "Assisted Pull-Up",
        "One-Arm Dumbbell Row (Light)",
        "Superman Hold",
        "Bird-Dog",
        "Reverse Snow Angel",
    ]
    exercises = Exercise.objects.exclude(name__in=hidden_seed_exercises)
    return render(request, 'exercise_library.html', {'exercises': exercises})

def training_session(request):
    return render(request, 'training.html')


@login_required
def live_training_dashboard(request):
    trainers = Trainer.objects.all()
    # Show upcoming available slots (not booked) for users to book.
    slots = (
        TrainingSlot.objects
        .select_related("trainer")
        .filter(is_booked=False, session_time__gte=timezone.now())
        .order_by("session_time")[:60]
    )

    # For "Your bookings" badge on cards:
    my_slots = (
        TrainingSlot.objects
        .select_related("trainer")
        .filter(booked_by=request.user)
        .order_by("-session_time")[:30]
    )
    latest_booked_by_trainer = {}
    for s in my_slots:
        if s.trainer_id not in latest_booked_by_trainer:
            latest_booked_by_trainer[s.trainer_id] = s

    trainer_cards = []
    for t in trainers:
        t_slots = [s for s in slots if s.trainer_id == t.id]
        trainer_cards.append({
            "trainer": t,
            "available_slots": t_slots[:5],
            "latest_booking": latest_booked_by_trainer.get(t.id),
        })

    return render(request, "live_training_dashboard.html", {
        "trainer_cards": trainer_cards,
        "now": timezone.now(),
    })


@login_required
@require_POST
def book_training_session(request, trainer_id):
    trainer = get_object_or_404(Trainer, id=trainer_id)
    slot_id = (request.POST.get("slot_id") or "").strip()
    if not slot_id:
        messages.error(request, "Please select a slot.")
        return redirect("live_training_dashboard")

    slot = get_object_or_404(TrainingSlot, id=slot_id, trainer=trainer)
    if slot.is_booked:
        messages.error(request, "That slot was already booked. Please choose another one.")
        return redirect("live_training_dashboard")

    slot.is_booked = True
    slot.booked_by = request.user
    slot.save(update_fields=["is_booked", "booked_by"])

    # Keep the existing TrainingSession table as a booking history record.
    TrainingSession.objects.create(
        trainer=trainer,
        user=request.user,
        session_time=slot.session_time,
        is_active=slot.is_active,
        meeting_link=slot.meeting_link,
    )

    messages.success(request, f"✅ Session booked with {trainer.name}. Wait for the trainer to activate it.")
    return redirect("live_training_dashboard")


@login_required
def live_training_room(request, session_id):
    # New flow uses TrainingSlot IDs (booked_by=user).
    slot = TrainingSlot.objects.select_related("trainer", "booked_by").filter(id=session_id).first()
    if slot:
        if slot.booked_by_id != request.user.id:
            return redirect("live_training_dashboard")
        return render(request, "live_training_room.html", {"session": slot})

    # Backward compatibility: older links may still point to TrainingSession IDs.
    session = get_object_or_404(
        TrainingSession.objects.select_related("trainer", "user"),
        id=session_id,
        user=request.user,
    )
    return render(request, "live_training_room.html", {"session": session})


@staff_member_required
@require_POST
def set_training_session_active(request, session_id):
    session = get_object_or_404(TrainingSession, id=session_id)
    is_active = (request.POST.get("is_active") or "").strip().lower() in ("1", "true", "yes", "on")
    session.is_active = is_active
    session.save(update_fields=["is_active"])
    return redirect("live_training_dashboard")


def _require_trainer_user(request):
    trainer = Trainer.objects.filter(user=request.user).first()
    return trainer


def trainer_login_redirect(request):
    return redirect("trainer_profile")


from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout


def trainer_login(request):
    if request.user.is_authenticated:
        trainer = Trainer.objects.filter(user=request.user).first()
        if trainer:
            return redirect("trainer_profile")

    if request.method == "POST":
        email = (request.POST.get("email") or "").strip()
        password = (request.POST.get("password") or "").strip()
        user = None
        if email and password:
            # Try username or email
            user = authenticate(request, username=email, password=password)
            if user is None:
                u = User.objects.filter(email__iexact=email).first()
                if u:
                    user = authenticate(request, username=u.username, password=password)
        if user is None:
            messages.error(request, "Invalid trainer credentials.")
            return render(request, "trainer/login.html")

        # Ensure this user is a trainer account
        if not Trainer.objects.filter(user=user).exists():
            messages.error(request, "This account is not a trainer account.")
            return render(request, "trainer/login.html")

        auth_login(request, user)
        return redirect("trainer_profile")

    return render(request, "trainer/login.html")


def trainer_logout(request):
    auth_logout(request)
    return redirect("trainer_login")


def trainer_profile(request):
    if not request.user.is_authenticated:
        return redirect("trainer_login")
    trainer = Trainer.objects.filter(user=request.user).first()
    if not trainer:
        return redirect("trainer_login")

    slots = TrainingSlot.objects.filter(trainer=trainer).order_by("-session_time")[:80]
    upcoming = TrainingSlot.objects.filter(trainer=trainer, session_time__gte=timezone.now()).order_by("session_time")[:20]
    booking_count = TrainingSlot.objects.filter(trainer=trainer, is_booked=True).count()

    return render(request, "trainer_profile.html", {
        "trainer": trainer,
        "slots": slots,
        "upcoming": upcoming,
        "booking_count": booking_count,
        "now": timezone.now(),
    })


@require_POST
def trainer_create_slot(request):
    if not request.user.is_authenticated:
        return redirect("trainer_login")
    trainer = Trainer.objects.filter(user=request.user).first()
    if not trainer:
        return redirect("trainer_login")

    raw_time = (request.POST.get("session_time") or "").strip()
    if not raw_time:
        messages.error(request, "Please select a session time.")
        return redirect("trainer_dashboard")

    try:
        naive_dt = datetime.datetime.strptime(raw_time, "%Y-%m-%dT%H:%M")
        session_time = timezone.make_aware(naive_dt, timezone.get_current_timezone())
    except Exception:
        messages.error(request, "Invalid date/time.")
        return redirect("trainer_dashboard")

    TrainingSlot.objects.create(
        trainer=trainer,
        session_time=session_time,
        is_active=False,
        meeting_link=TrainingSlot.generate_meeting_link(),
        is_booked=False,
        booked_by=None,
    )
    messages.success(request, "✅ Slot created successfully.")
    return redirect("trainer_profile")


@require_POST
def trainer_toggle_slot_active(request, slot_id):
    if not request.user.is_authenticated:
        return redirect("trainer_login")
    trainer = Trainer.objects.filter(user=request.user).first()
    if not trainer:
        return redirect("trainer_login")

    slot = get_object_or_404(TrainingSlot, id=slot_id, trainer=trainer)
    is_active = (request.POST.get("is_active") or "").strip().lower() in ("1", "true", "yes", "on")
    slot.is_active = is_active
    slot.save(update_fields=["is_active"])
    messages.success(request, "✅ Session status updated.")
    return redirect("trainer_profile")


def trainer_start_session(request, slot_id):
    if not request.user.is_authenticated:
        return redirect("trainer_login")
    trainer = Trainer.objects.filter(user=request.user).first()
    if not trainer:
        return redirect("trainer_login")

    slot = get_object_or_404(TrainingSlot.objects.select_related("booked_by"), id=slot_id, trainer=trainer)
    return render(request, "trainer_start_session.html", {"trainer": trainer, "slot": slot})


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
            has_user_field = any(field.name == 'user' for field in DietPlan._meta.fields)

            payload = {
                'title': data.get('title', 'AI Plan'),
                'breakfast': data.get('breakfast', 'Healthy meal'),
                'lunch': data.get('lunch', 'Healthy meal'),
                'dinner': data.get('dinner', 'Healthy meal')
            }
            payload['calories'] = _compute_total_plan_calories(
                payload['breakfast'],
                payload['lunch'],
                payload['dinner'],
                fallback=data.get('calories', 2000)
            )

            if has_user_field:
                if not request.user.is_authenticated:
                    return JsonResponse({'status': 'error', 'message': 'User not logged in'})
                payload['user'] = request.user

            DietPlan.objects.create(**payload)

            # Keep AI memory in sync with real DB state.
            if request.user.is_authenticated:
                mem, _ = MemberMemory.objects.get_or_create(user=request.user)
                facts = mem.ai_facts or {}
                facts["diet_plan_exists"] = True
                mem.ai_facts = facts
                mem.save()

            return JsonResponse({
                'status': 'success',
                'message': 'Plan saved successfully!'
            })

        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            })

    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)



# 🟢 DELETE DIET PLAN
@csrf_exempt
def delete_diet_plan_ai(request):
    if request.method == 'POST':
        try:
            payload = json.loads(request.body or "{}")
            scope = str(payload.get("scope", "all")).lower()
            has_user_field = any(field.name == 'user' for field in DietPlan._meta.fields)

            if has_user_field:
                if not request.user.is_authenticated:
                    return JsonResponse({'status': 'error', 'message': 'User not logged in'})
                qs = DietPlan.objects.filter(user=request.user).order_by('-id')
            else:
                # For current schema (no user column), operate on all plans.
                qs = DietPlan.objects.all().order_by('-id')

            if scope == "latest":
                latest_plan = qs.first()
                if latest_plan:
                    deleted_count, _ = latest_plan.delete()
                else:
                    deleted_count = 0
            else:
                deleted_count, _ = qs.delete()

            # Keep AI memory/session aligned after deletion.
            if request.user.is_authenticated:
                mem, _ = MemberMemory.objects.get_or_create(user=request.user)
                facts = mem.ai_facts or {}
                facts["diet_plan_exists"] = False
                mem.ai_facts = facts
                mem.save()
            request.session['chat_history_list'] = []

            if deleted_count > 0:
                return JsonResponse({
                    'status': 'success',
                    'message': f'{deleted_count} plan(s) deleted successfully'
                })
            else:
                return JsonResponse({
                    'status': 'no_plan',
                    'message': 'No plan found to delete'
                })

        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            })

    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)