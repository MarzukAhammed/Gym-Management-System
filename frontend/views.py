from django.shortcuts import render, redirect, get_object_or_404
from .models import Plan, Trainer, Member, Review, TrainerReview, SuccessStory, Profile, GalleryMember, DietPlan, TrainingSession, Notification, TrainingSlot, DailyChallenge, ChallengeSubmission, UserChallengeProfile, ChallengeVideoComment
from .forms import MemberForm, SignupForm, JoinForm, ContactForm, ReviewForm, TrainerReviewForm, ProfileForm, SuccessStoryForm
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import MemberUpdateForm
from django.http import StreamingHttpResponse
from .camera import PushUpDetector
from django.http import JsonResponse
from .models import HealthMemory, MemberMemory, Exercise, UserProgress
from .ai_engine import SmartCoach, detect_language_mode
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
import json, datetime
import re
from decimal import Decimal, InvalidOperation
from pathlib import Path
from functools import lru_cache
from django.conf import settings
from django.db import models
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import Paginator
from django.urls import reverse
from .challenges import ensure_active_challenges

def _user_has_verified_subscription(user):
    """
    Subscription = user has a Member plan AND a verified Payment.
    """
    try:
        member = getattr(user, "member", None)
        if not member or not getattr(member, "plan", None):
            return False

        # Check for verified payment directly linked to user or matching username
        from .models import ManualPayment
        return ManualPayment.objects.filter(
            models.Q(user=user) | models.Q(full_name__iexact=user.username),
            verified=True
        ).exists()
    except Exception:
        return False

# Home Page
def home(request):
    # Auto-generate challenges on fresh DBs (e.g., switching PCs).
    # Keeps the UI from showing "No challenges found" and removes the need to run seed manually.
    try:
        ensure_active_challenges(min_per_day=7)
    except Exception:
        # Never block homepage if generation fails for any reason.
        pass

    plans = Plan.objects.all()
    trainers = Trainer.objects.all()
    reviews = Review.objects.select_related("user").order_by("-created_at")[:5]
    for review in reviews:
        review.member = getattr(review.user, "member", None)
    success_stories = SuccessStory.objects.order_by("-created_at")[:6]
    today_idx = timezone.localdate().weekday()
    todays_challenges = DailyChallenge.objects.filter(is_active=True, day_of_week=today_idx)
    all_week_challenges = DailyChallenge.objects.filter(is_active=True).order_by("day_of_week", "id")
    feed = (
        ChallengeSubmission.objects
        .select_related("user", "challenge")
        .order_by("-created_at")[:10]
    )
    return render(request, "index.html", {
        "plans": plans,
        "trainers": trainers,
        "reviews": reviews,
        "success_stories": success_stories,
        "todays_challenges": todays_challenges,
        "all_week_challenges": all_week_challenges,
        "today_idx": today_idx,
        "challenge_feed": feed,
    })

# Signup
def signup(request):
    if request.user.is_authenticated:
        if _user_has_verified_subscription(request.user):
            messages.info(request, "You are already logged in and already have an active subscription.")
            return redirect("profile")
        messages.info(request, "You are already logged in.")
        return redirect("home")

    if request.method == "POST":
        # Step 1 - user submitted signup form
        if 'otp' not in request.POST:
            form = SignupForm(request.POST)
            if form.is_valid():
                user = form.save(commit=False)
                user.is_active = False
                user.save()
                # Generate 6 digit OTP
                from frontend.models import EmailVerificationToken
                import random
                code = str(random.randint(100000, 999999))
                EmailVerificationToken.objects.update_or_create(
                    user=user,
                    defaults={'token': code}
                )
                # Send email
                from django.core.mail import send_mail
                from django.conf import settings
                send_mail(
                    'Verify your Gym Account',
                    f'Your verification code is: {code}\n\nThis code expires in 30 minutes.',
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                )
                request.session['verify_user_id'] = user.id
                return render(request, 'signup.html', {
                    'form': form,
                    'show_otp': True,
                    'email': user.email
                })
            else:
                return render(request, 'signup.html', {'form': form})

        # Step 2 - user submitted OTP
        if 'otp' in request.POST:
            user_id = request.session.get('verify_user_id')
            otp_input = request.POST.get('otp')
            from frontend.models import EmailVerificationToken
            from django.contrib.auth.models import User
            try:
                user = User.objects.get(id=user_id)
                token_obj = EmailVerificationToken.objects.get(user=user)
                if token_obj.is_valid() and token_obj.token == otp_input:
                    user.is_active = True
                    user.save()
                    token_obj.delete()
                    del request.session['verify_user_id']
                    messages.success(request, "Email verified! You can now log in.")
                    return redirect('login')
                else:
                    return render(request, 'signup.html', {
                        'show_otp': True,
                        'email': user.email,
                        'error': 'Invalid or expired code. Please try again.'
                    })
            except Exception:
                return render(request, 'signup.html', {
                    'error': 'Something went wrong. Please sign up again.'
                })

    else:
        # Clear any previous verification session if user comes back to signup
        if 'verify_user_id' in request.session:
            # Delete the inactive user and token if they go back
            from django.contrib.auth.models import User
            from frontend.models import EmailVerificationToken
            try:
                old_user = User.objects.get(id=request.session['verify_user_id'])
                EmailVerificationToken.objects.filter(user=old_user).delete()
                old_user.delete()
            except Exception:
                pass
            del request.session['verify_user_id']
        form = SignupForm()
    return render(request, 'signup.html', {'form': form})

# Join Now
def join_now(request):
    if request.user.is_authenticated:
        if _user_has_verified_subscription(request.user):
            messages.info(request, "You are already logged in and already have an active subscription.")
            return redirect("profile")
        # If they already filled join details (Member exists + plan chosen), take them to payment.
        existing_member = getattr(request.user, "member", None)
        if existing_member and getattr(existing_member, "plan", None):
            # Try to find the plan by title to get its ID
            plan_title = existing_member.plan
            try:
                plan = Plan.objects.get(title=plan_title)
                messages.info(request, "Complete payment to activate your subscription.")
                return redirect(f'/payment/?plan={plan.id}')
            except Plan.DoesNotExist:
                messages.info(request, "Complete payment to activate your subscription.")
                return redirect("payment")
        # Otherwise let them fill the join form (we can preselect plan from query param).

    if request.method == 'POST':
        form = JoinForm(request.POST, request.FILES)
        if form.is_valid():
            email = form.cleaned_data['email']
            if Member.objects.filter(email=email).exists():
                messages.error(request, "A member with this email already exists.")
            else:
                # Get plan_id from form before saving
                plan_id = form.cleaned_data.get('plan')
                member = form.save(commit=False)
                if request.user.is_authenticated:
                    member.user = request.user
                member.save()
                messages.success(request, "🎉 You have successfully joined our gym!")
                # Redirect to payment with the plan_id directly from form
                if plan_id:
                    return redirect(f'/payment/?plan={plan_id}')
                else:
                    return redirect('payment')
    else:
        initial = {}
        if request.user.is_authenticated and getattr(request.user, "email", None):
            initial["email"] = request.user.email
        plan_id = (request.GET.get("plan") or "").strip()
        if plan_id.isdigit():
            try:
                plan = Plan.objects.get(id=int(plan_id))
                initial["plan"] = plan.id
            except Plan.DoesNotExist:
                pass
        form = JoinForm(initial=initial)

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
    
    # NEW logic: use the direct user link for payment verification.
    # We still fallback to username-based match for legacy payments if needed,
    # but the primary check is the user ForeignKey.
    from .models import ManualPayment
    payment_qs = ManualPayment.objects.filter(
        models.Q(user=request.user) | models.Q(full_name__iexact=request.user.username)
    )
    verified_payment = payment_qs.filter(
        verified=True
    ).exists()
    pending_payment_submission = payment_qs.filter(
        verified=False
    ).exists()

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
        return raw_name

    clean_plan_name = _resolve_plan_name(member.plan) if member else None
    display_plan_name = _friendly_plan_name(clean_plan_name) if clean_plan_name else None
    selected_plan = display_plan_name if display_plan_name and verified_payment else None
    # Show "pending verification" only after a real payment submission exists.
    pending_plan = display_plan_name if display_plan_name and pending_payment_submission and not verified_payment else None
    return render(request, 'profile.html', {
        'profile': profile,
        'selected_plan': selected_plan,
        'pending_plan': pending_plan,
    })

# About, Plans, Team, Gallery
def about(request): return render(request, "about.html")
def plans_page(request): return render(request, "plans.html", {"plans": Plan.objects.all()})
@login_required
def team(request):
    q = (request.GET.get("q") or "").strip()
    qs = (
        ChallengeSubmission.objects
        .select_related("user", "challenge")
        .prefetch_related("comments", "comments__user")
        .order_by("-created_at")
    )
    if q:
        qs = qs.filter(
            models.Q(user__username__icontains=q)
            | models.Q(challenge__title__icontains=q)
        )

    paginator = Paginator(qs, 12)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(request, "team.html", {
        "page_obj": page_obj,
        "q": q,
    })


@login_required
@require_POST
def add_challenge_video_comment(request, submission_id):
    submission = get_object_or_404(ChallengeSubmission, id=submission_id)
    text = (request.POST.get("text") or "").strip()
    if not text:
        messages.error(request, "Comment cannot be empty.")
        return redirect(f"{reverse('team')}#video-{submission_id}")

    comment = ChallengeVideoComment.objects.create(
        submission=submission,
        user=request.user,
        text=text[:1000],
    )
    # Notify the video owner (if someone else commented)
    if submission.user_id and submission.user_id != request.user.id:
        Notification.objects.create(
            user=submission.user,
            level="info",
            text=f"💬 {request.user.username} commented on your challenge video: “{comment.text[:120]}”.",
            is_read=False,
        )
    messages.success(request, "Comment posted.")
    return redirect(f"{reverse('team')}#video-{submission_id}")


@login_required
@require_POST
def edit_challenge_video_comment(request, comment_id):
    c = get_object_or_404(ChallengeVideoComment, id=comment_id)
    if not (request.user.is_staff or c.user_id == request.user.id):
        return JsonResponse({"status": "error", "message": "Not allowed"}, status=403)

    text = (request.POST.get("text") or "").strip()
    if not text:
        return JsonResponse({"status": "error", "message": "Comment cannot be empty"}, status=400)

    c.text = text[:1000]
    c.save(update_fields=["text"])
    return JsonResponse({"status": "success", "text": c.text})


@login_required
@require_POST
def delete_challenge_video_comment(request, comment_id):
    c = get_object_or_404(ChallengeVideoComment, id=comment_id)
    if not (request.user.is_staff or c.user_id == request.user.id):
        return JsonResponse({"status": "error", "message": "Not allowed"}, status=403)

    submission_id = c.submission_id
    c.delete()
    return JsonResponse({"status": "success", "submission_id": submission_id})
def gallery(request): return render(request, "gallery.html", {"members": GalleryMember.objects.all()})
def privacy_policy(request): return render(request, "privacy_policy.html")
def terms_conditions(request): return render(request, "terms_conditions.html")
def refund_policy(request): return render(request, "refund_policy.html")


@login_required
def daily_challenge_record(request, challenge_id):
    challenge = get_object_or_404(DailyChallenge, id=challenge_id, is_active=True)
    today_idx = timezone.localdate().weekday()
    if challenge.day_of_week != today_idx:
        messages.error(request, "That challenge is not scheduled for today.")
        return redirect("home")
    return render(request, "daily_challenge_record.html", {"challenge": challenge})


@login_required
@require_POST
def daily_challenge_submit(request, challenge_id):
    challenge = get_object_or_404(DailyChallenge, id=challenge_id, is_active=True)
    today = timezone.localdate()
    if challenge.day_of_week != today.weekday():
        return JsonResponse({"status": "error", "message": "Not today's challenge."}, status=400)

    video = request.FILES.get("video")
    if not video:
        return JsonResponse({"status": "error", "message": "Video required."}, status=400)

    prof, _ = UserChallengeProfile.objects.get_or_create(user=request.user)
    # Prevent multiple submissions counting for streak in same day; still keep the submission for feed.
    already_done_today = (prof.last_completed_date == today)

    coins = 0 if already_done_today else int(challenge.coins_reward or 0)
    submission = ChallengeSubmission.objects.create(
        challenge=challenge,
        user=request.user,
        proof_video=video,
        coins_granted=coins,
    )

    if not already_done_today:
        if prof.last_completed_date == (today - datetime.timedelta(days=1)):
            prof.current_streak += 1
        else:
            prof.current_streak = 1
        prof.last_completed_date = today
        # Streak updates immediately; coins require admin approval.
        prof.save(update_fields=["current_streak", "last_completed_date"])

        if coins > 0:
            Notification.objects.create(
                user=request.user,
                level="info",
                text=f"⏳ Submission received for '{challenge.title}'. Coins pending admin approval (+{coins}).",
                is_read=False,
            )

    return JsonResponse({
        "status": "success",
        "submission_id": submission.id,
        "coins_granted": 0,
        "coins_pending": coins,
        "current_streak": prof.current_streak,
        "gym_coins": prof.gym_coins,
    })

def gallery_detail(request, id):
    member = get_object_or_404(GalleryMember, id=id)
    return render(request, "gallery_detail.html", {"member": member})

def testimonial(request):
    q = (request.GET.get("trainer") or "").strip()
    qs = TrainerReview.objects.select_related("user", "trainer").all()
    if q.isdigit():
        qs = qs.filter(trainer_id=int(q))
    trainers = Trainer.objects.all().order_by("name")
    return render(request, "testimonial.html", {
        "reviews": qs,
        "trainers": trainers,
        "active_trainer_id": int(q) if q.isdigit() else None,
    })

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
    # Trainer reviews (1 per user per trainer)
    if request.method == "POST":
        form = TrainerReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.rating = int(review.rating or 5)
            try:
                review.save()
            except Exception:
                # likely unique_together violation
                TrainerReview.objects.filter(trainer=review.trainer, user=request.user).update(
                    rating=review.rating, comment=review.comment
                )
            messages.success(request, "✅ Trainer review saved!")
            return redirect("testimonial")
    return render(request, "add_review.html", {"form": TrainerReviewForm()})

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


def _wants_to_save_diet_plan(user_text):
    text = (user_text or "").lower()
    print(f"DEBUG: _wants_to_save_diet_plan checking: '{text}'")
    triggers = (
        "save this plan",
        "save this to diet",
        "save this to my diet",
        "save this plan to my diet",
        "save to diet",
        "save to my diet",
        "save it to my diet",
        "save my diet plan",
        "save diet",
        "add diet",
        "save this diet",
        "add this diet",
        "save meal plan",
        "add meal plan",
        "save plan",
        "add plan to diet",
        # Banglish intents
        "diet plan save",
        "diet save",
        "diet add",
        "diet plan add",
        "diet plan save koro",
        "diet plan add koro",
        "diet ta save koro",
        "diet ta add koro",
        "save kore dao",
        "add kore dao",
        "save kore den",
        "add kore den",
        "save kore din",
        "add kore din",
        "plan ta save koro",
        "plan ta add koro",
        "eta save koro",
        "eta diet e save koro",
        "diet plan e save koro",
    )
    found_triggers = [t for t in triggers if t in text]
    result = any(t in text for t in triggers)
    print(f"DEBUG: Found triggers: {found_triggers}")
    print(f"DEBUG: _wants_to_save_diet_plan result: {result}")
    return result


def _extract_meal_line(reply_text, label):
    print(f"DEBUG: _extract_meal_line called with reply_text: '{reply_text}', label: '{label}'")
    if not reply_text:
        print("DEBUG: reply_text is empty, returning empty string")
        return ""
    # Accept both `Breakfast: ...` and `Breakfast - ...`
    pattern = rf"{label}\s*[:\-]\s*(.+?)(?=\b(?:breakfast|lunch|dinner)\s*[:\-]|Total:|$)"
    print(f"DEBUG: pattern: {pattern}")
    m = re.search(pattern, str(reply_text), flags=re.IGNORECASE | re.DOTALL)
    print(f"DEBUG: regex match result: {m}")
    if not m:
        print("DEBUG: No match found, returning empty string")
        return ""
    result = re.sub(r"\s+", " ", m.group(1)).strip(" .")
    print(f"DEBUG: extracted meal: '{result}'")
    return result


def _extract_diet_payload_from_ai(ai_json):
    print(f"DEBUG: _extract_diet_payload_from_ai called with ai_json: {ai_json}")
    
    if not isinstance(ai_json, dict):
        print("DEBUG: ai_json is not a dict, returning None")
        return None

    facts = ai_json.get("new_facts") if isinstance(ai_json.get("new_facts"), dict) else {}
    nested = facts.get("diet_plan") if isinstance(facts.get("diet_plan"), dict) else {}
    reply_text = ai_json.get("reply", "")
    
    print(f"DEBUG: facts: {facts}")
    print(f"DEBUG: nested: {nested}")
    print(f"DEBUG: reply_text: {reply_text}")

    # Try structured fields first, then parse from reply text.
    title = (
        nested.get("title")
        or facts.get("diet_plan_title")
        or facts.get("title")
        or "AI Diet Plan"
    )
    breakfast = (
        nested.get("breakfast")
        or facts.get("diet_breakfast")
        or facts.get("breakfast")
        or _extract_meal_line(reply_text, "breakfast")
    )
    lunch = (
        nested.get("lunch")
        or facts.get("diet_lunch")
        or facts.get("lunch")
        or _extract_meal_line(reply_text, "lunch")
    )
    dinner = (
        nested.get("dinner")
        or facts.get("diet_dinner")
        or facts.get("dinner")
        or _extract_meal_line(reply_text, "dinner")
    )
    calories = (
        nested.get("calories")
        or facts.get("diet_calories")
        or facts.get("calories")
    )
    
    print(f"DEBUG: Extracted - title: {title}, breakfast: {breakfast}, lunch: {lunch}, dinner: {dinner}, calories: {calories}")

    if not any([breakfast, lunch, dinner]):
        print("DEBUG: No meals found, returning None")
        return None

    payload = {
        "title": str(title).strip() or "AI Diet Plan",
        "breakfast": str(breakfast or "Healthy breakfast").strip(),
        "lunch": str(lunch or "Healthy lunch").strip(),
        "dinner": str(dinner or "Healthy dinner").strip(),
        "calories": calories,
    }
    print(f"DEBUG: Returning payload: {payload}")
    return payload


def _extract_json_object_loose(text):
    text = (text or "").strip()
    try:
        return json.loads(text)
    except Exception:
        pass
    try:
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            return json.loads(text[start:end + 1])
    except Exception:
        pass
    return None


def _save_diet_plan_record(payload, mem=None, request_user=None):
    print(f"DEBUG: _save_diet_plan_record called with payload: {payload}")
    print(f"DEBUG: request_user: {request_user}, is_authenticated: {request_user.is_authenticated if request_user else 'None'}")
    
    computed_calories = _compute_total_plan_calories(
        payload["breakfast"],
        payload["lunch"],
        payload["dinner"],
        fallback=payload.get("calories", 2000),
    )
    print(f"DEBUG: computed_calories: {computed_calories}")
    
    # Associate diet plan with user if authenticated
    user = request_user if (request_user and request_user.is_authenticated) else None
    print(f"DEBUG: user for diet plan: {user}")
    
    try:
        diet_plan = DietPlan.objects.create(
            user=user,
            title=payload["title"],
            breakfast=payload["breakfast"],
            lunch=payload["lunch"],
            dinner=payload["dinner"],
            calories=computed_calories,
        )
        print(f"DEBUG: DietPlan created successfully with ID: {diet_plan.id}")
    except Exception as e:
        print(f"DEBUG: Error creating DietPlan: {e}")
        raise e
    
    if mem is not None and request_user is not None and request_user.is_authenticated:
        facts = mem.ai_facts or {}
        facts["diet_plan_exists"] = True
        mem.ai_facts = facts
        mem.save()
        print(f"DEBUG: Updated memory with diet_plan_exists=True")


def _extract_latest_assistant_reply(raw_history):
    entries = raw_history or []
    for line in reversed(entries):
        if isinstance(line, str) and line.startswith("Elina:"):
            return line.split("Elina:", 1)[1].strip()
    return ""


def _extract_latest_user_message(raw_history):
    entries = raw_history or []
    for line in reversed(entries):
        if isinstance(line, str) and line.startswith("User:"):
            return line.split("User:", 1)[1].strip()
    return ""


def _wants_a_diet_plan_generation(user_text):
    text = (user_text or "").lower()
    triggers = (
        "diet plan",
        "make diet",
        "generate diet",
        "create diet",
        "meal plan",
        "food plan",
        "diet chart",
        "diet bana",
        "diet banai",
        "diet dao",
        "diet den",
        "meal plan dao",
    )
    return any(t in text for t in triggers) and not _wants_to_save_diet_plan(text)


def _quick_diet_payload_for_user(request):
    print(f"DEBUG: _quick_diet_payload_for_user called for user: {request.user}")
    profile = getattr(request.user, "profile", None) if request.user.is_authenticated else None
    print(f"DEBUG: profile: {profile}")
    goal = (getattr(profile, "fitness_goal", "") or "").lower() if profile else ""
    weight = getattr(profile, "weight", None) if profile else None
    print(f"DEBUG: goal: '{goal}', weight: {weight}")
    calories = 2000
    if isinstance(weight, (int, float)) and weight > 0:
        calories = int(max(1500, min(3200, weight * 30)))
    if "loss" in goal or "cut" in goal or "fat" in goal:
        calories = max(1400, calories - 250)
        title = "Fat Loss Diet Plan"
    elif "gain" in goal or "bulk" in goal or "muscle" in goal:
        calories = min(3600, calories + 250)
        title = "Muscle Gain Diet Plan"
    else:
        title = "Balanced Diet Plan"

    breakfast = "2 eggs, 1 banana, 1 glass milk (~500 kcal)"
    lunch = "Rice (moderate), lentils, chicken breast, mixed vegetables (~800 kcal)"
    dinner = "Fish/chicken, vegetables, small rice/roti portion (~700 kcal)"
    
    payload = {
        "title": title,
        "breakfast": breakfast,
        "lunch": lunch,
        "dinner": dinner,
        "calories": calories,
    }
    print(f"DEBUG: quick diet payload: {payload}")
    return payload


def _should_use_site_context(user_msg):
    q = (user_msg or "").lower()
    site_keywords = (
        "website", "site", "page", "pricing", "plan", "membership", "trainer",
        "payment", "contact", "policy", "refund", "terms", "gym",
    )
    return any(k in q for k in site_keywords)


def _should_allow_internet_search(user_msg):
    q = (user_msg or "").lower()
    search_triggers = (
        "latest", "today", "current", "news", "update", "recent", "price today",
    )
    return any(t in q for t in search_triggers)


def _parse_diet_delete_intent(user_text):
    text = (user_text or "").lower().strip()
    if not text:
        return None

    # Must be a diet-plan deletion request.
    delete_words = ("delete", "remove", "muchi", "muche", "mush", "delete koro", "delete kore", "muchen", "mushun")
    diet_words = ("diet", "meal plan", "diet plan", "plan")
    if not (any(w in text for w in delete_words) and any(w in text for w in diet_words)):
        return None

    # Delete all
    if (
        "delete all" in text
        or "all diet" in text
        or "all plans" in text
        or "sob diet" in text
        or "shob diet" in text
        or "sob plan" in text
        or "shob plan" in text
        or "all delete" in text
    ):
        return {"scope": "all", "index": None}

    # Delete specific numbered plan.
    m = re.search(r"(?:diet\s*plan|plan|diet)\s*#?\s*(\d+)", text)
    if m:
        return {"scope": "index", "index": int(m.group(1))}
    m2 = re.search(r"#\s*(\d+)", text)
    if m2:
        return {"scope": "index", "index": int(m2.group(1))}

    # Fallback: delete latest.
    return {"scope": "latest", "index": None}


def _apply_diet_delete_intent(user_text, request, mem, language_mode):
    intent = _parse_diet_delete_intent(user_text)
    if not intent:
        return None

    scope = intent["scope"]
    index = intent["index"]
    has_user_field = any(field.name == 'user' for field in DietPlan._meta.fields)

    if has_user_field:
        if not request.user.is_authenticated:
            return "Login first to manage your diet plans."
        base_qs = DietPlan.objects.filter(user=request.user)
    else:
        base_qs = DietPlan.objects.all()

    plans_ordered = list(base_qs.order_by("id"))
    total = len(plans_ordered)

    deleted_count = 0
    message = ""
    if scope == "all":
        deleted_count, _ = base_qs.delete()
        message = f"Deleted all {deleted_count} diet plan(s)."
    elif scope == "index":
        n = int(index or 0)
        if n < 1 or n > total:
            return f"Plan #{n} does not exist. You currently have {total} plan(s)."
        plan = plans_ordered[n - 1]
        title = plan.title
        plan.delete()
        deleted_count = 1
        message = f'Deleted plan #{n}: "{title}".'
    else:
        if not plans_ordered:
            deleted_count = 0
            message = "No diet plan found to delete."
        else:
            plan = plans_ordered[-1]
            title = plan.title
            plan.delete()
            deleted_count = 1
            message = f'Deleted latest plan: "{title}" (was #{total}).'

    if request.user.is_authenticated:
        facts = mem.ai_facts or {}
        if has_user_field:
            facts["diet_plan_exists"] = DietPlan.objects.filter(user=request.user).exists()
        else:
            facts["diet_plan_exists"] = DietPlan.objects.exists()
        mem.ai_facts = facts
        mem.save()
    request.session['chat_history_list'] = []

    if language_mode != "english":
        if scope == "all":
            return f"Diet plan delete successful. Sob diet plan delete kore disi. ({deleted_count} ta)"
        if scope == "index" and deleted_count:
            return f"Diet plan delete successful. {message.replace('Deleted', 'Delete kore disi')}"
        if scope == "latest" and deleted_count:
            return "Diet plan delete successful. Latest diet plan delete kore disi."
        return "Delete korar moto kono diet plan pelam na."
    if deleted_count > 0:
        return f"Diet plan deleted successfully. {message}"
    return message


@login_required
def diet(request):
    if request.user.is_authenticated:
        plans = DietPlan.objects.filter(user=request.user).order_by("id")
    else:
        plans = DietPlan.objects.none()  # No diet plans for non-authenticated users
    for plan in plans:
        # Always show computed calories from meal lines when available.
        plan.display_calories = _compute_total_plan_calories(
            plan.breakfast,
            plan.lunch,
            plan.dinner,
            fallback=plan.calories
        )
    return render(request, 'diet.html', {'plans': plans})

def payment(request, plan_name=None):
    if request.method == "POST":
        print(f"DEBUG: Payment POST received")
        print(f"DEBUG: POST data: {request.POST}")
        amount = request.POST.get("amount")
        sender_number = (request.POST.get("sender_number") or "").strip()
        reference_username = (request.POST.get("reference_username") or "").strip()
        trx_id = request.POST.get("trx_id")
        plan_id = (request.POST.get("plan_id") or "").strip()
        plan_id_query = (request.GET.get("plan") or "").strip()
        print(f"DEBUG: Extracted - amount: {amount}, sender_number: {sender_number}, reference_username: {reference_username}, trx_id: {trx_id}, plan_id: {plan_id}")

        selected_plan = None
        # Accept selected plan either from form dropdown or legacy ?plan= query.
        effective_plan_id = plan_id if plan_id.isdigit() else (plan_id_query if plan_id_query.isdigit() else "")
        if effective_plan_id:
            plan_id = effective_plan_id
            selected_plan = Plan.objects.filter(id=int(plan_id)).first()
        if not selected_plan:
            selected_plan = Plan.objects.order_by("id").first()
        if not selected_plan:
            messages.error(request, "No membership plans are configured yet.")
            return redirect("payment")

        # Keep amount in sync with selected plan and match ManualPayment.amount (IntegerField).
        try:
            amount = int(Decimal(str(selected_plan.price)))
        except (InvalidOperation, TypeError, ValueError):
            messages.error(request, "Selected plan price is invalid. Please try again.")
            return redirect("payment")

        # Use authenticated user as authoritative payment owner/reference.
        user = request.user if request.user.is_authenticated else None
        if user:
            reference_username = user.username

        if not amount or not sender_number or (not user and not reference_username):
            messages.error(request, "Please fill all required payment details.")
            return redirect("payment")

        from .models import ManualPayment
        ManualPayment.objects.create(
            user=user,
            full_name=reference_username,
            phone=sender_number,
            amount=amount,
            method="bkash",
            transaction_id=trx_id or f"REF-{reference_username}-{sender_number}"
        )
        messages.success(request, "Payment submitted. Verification is pending admin approval.")
        print("DEBUG: About to redirect to payment_success")
        return redirect("payment_success")

    default_username = request.user.username if request.user.is_authenticated else ""
    all_plans = Plan.objects.all().order_by("id")
    
    # Get selected plan from URL parameter or query parameter (fallback)
    selected_plan = None
    if plan_name:
        try:
            selected_plan = Plan.objects.get(title__iexact=plan_name)
        except Plan.DoesNotExist:
            pass
    else:
        # Fallback to query parameter for backward compatibility
        plan_id = request.GET.get("plan")
        if plan_id and plan_id.isdigit():
            try:
                selected_plan = Plan.objects.get(id=int(plan_id))
            except Plan.DoesNotExist:
                pass
    
    if not selected_plan:
        selected_plan = all_plans.first()

    return render(request, "payment.html", {
        "default_username": default_username,
        "selected_plan": selected_plan,
        "plans": all_plans,
        "selected_plan_id": str(selected_plan.id) if selected_plan else "",
    })



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
def clear_all_notifications(request):
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "POST only"}, status=405)
    try:
        Notification.objects.filter(user=request.user).delete()
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
    print(f"DEBUG: chat_with_ai called with user_msg: '{user_msg}'")
    language_mode = detect_language_mode(user_msg)
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
    # Each "turn" is user line + assistant line; used so the cat warms up the longer they chat
    prior_turns = max(0, len(raw_history) // 2)
    history_text = " | ".join(raw_history[-3:]) if raw_history else "None"
    site_context = _build_relevant_site_context(user_msg) if _should_use_site_context(user_msg) else ""
    profile_context = _build_profile_context(request)
    auth_flag = "true" if request.user.is_authenticated else "false"
    auth_line = f"Auth: logged_in={auth_flag}; username={request.user.username if request.user.is_authenticated else 'Guest'}"
    # Context (auth, profile, site) is passed inside SmartCoach system prompt; user message stays clean
    # so the model answers the actual question instead of fighting long duplicated instructions.

    # Fast path: direct diet deletion by user command from chat.
    delete_msg = _apply_diet_delete_intent(user_msg, request, mem, language_mode)
    if delete_msg:
        history = request.session.get('chat_history_list', [])
        history.append(f"User: {user_msg}")
        history.append(f"Elina: {delete_msg}")
        request.session['chat_history_list'] = history[-10:]
        return JsonResponse({'reply': delete_msg})

    # Fast path: save current/previous diet plan from chat without another heavy AI roundtrip.
    wants_save = _wants_to_save_diet_plan(user_msg)
    print(f"DEBUG: _wants_to_save_diet_plan('{user_msg}') = {wants_save}")
    if wants_save:
        print(f"DEBUG: User wants to save diet plan. user_msg: '{user_msg}'")
        print(f"DEBUG: raw_history: {raw_history}")
        
        latest_assistant_reply = _extract_latest_assistant_reply(raw_history)
        print(f"DEBUG: latest_assistant_reply: '{latest_assistant_reply}'")
        
        payload = _extract_diet_payload_from_ai({
            "reply": latest_assistant_reply,
            "new_facts": {},
        })
        print(f"DEBUG: payload from assistant reply: {payload}")
        
        if not payload:
            latest_user_msg = _extract_latest_user_message(raw_history)
            print(f"DEBUG: latest_user_msg: '{latest_user_msg}'")
            payload = _extract_diet_payload_from_ai({
                "reply": latest_user_msg,
                "new_facts": {},
            })
            print(f"DEBUG: payload from user message: {payload}")
            
        if not payload:
            # If no structured diet plan found in history, create a default one for the user
            print("DEBUG: Creating quick diet payload as fallback")
            payload = _quick_diet_payload_for_user(request)
            print(f"DEBUG: quick diet payload: {payload}")
            
        if payload:
            try:
                print("DEBUG: Attempting to save diet plan...")
                print(f"DEBUG: request.user: {request.user}")
                print(f"DEBUG: request.user.is_authenticated: {request.user.is_authenticated}")
                _save_diet_plan_record(payload, mem=mem, request_user=request.user)
                save_msg = (
                    "👍 Diet plan saved successfully! Check your Diet page."
                    if language_mode == "english"
                    else "👍 Diet plan successfully save hoyeche. Diet page e peye jabe."
                )
                print("DEBUG: Diet plan saved successfully!")
                # Verify it was actually saved
                if request.user.is_authenticated:
                    count = DietPlan.objects.filter(user=request.user).count()
                    print(f"DEBUG: User now has {count} diet plans")
            except Exception as e:
                import traceback
                print(f"DEBUG: Error saving diet plan: {e}")
                print(f"DEBUG: Full traceback: {traceback.format_exc()}")
                save_msg = (
                    f"Error saving diet plan: {str(e)}"
                    if language_mode == "english"
                    else f"Diet plan save korar somoy error hoyeche: {str(e)}"
                )
        else:
            print("DEBUG: No payload found, cannot save")
            save_msg = (
                "Could not find a valid breakfast/lunch/dinner plan to save. Ask for a full diet plan first, then say save."
                if language_mode == "english"
                else "Save korar jonno valid breakfast/lunch/dinner plan pelam na. Age full diet plan nao, tarpor save bolo."
            )
        history = request.session.get('chat_history_list', [])
        history.append(f"User: {user_msg}")
        history.append(f"Elina: {save_msg}")
        request.session['chat_history_list'] = history[-10:]
        return JsonResponse({'reply': save_msg})

    # Only use fast path for very simple diet requests, let AI handle more complex ones
    if _wants_a_diet_plan_generation(user_msg) and len(user_msg.split()) <= 3:
        payload = _quick_diet_payload_for_user(request)
        diet_reply = (
            f"{payload['title']}\n"
            f"Breakfast: {payload['breakfast']}\n"
            f"Lunch: {payload['lunch']}\n"
            f"Dinner: {payload['dinner']}\n"
            f"Total: ~{payload['calories']} kcal.\n"
            "Say 'save this plan to my diet' and I will save it."
        )
        history = request.session.get('chat_history_list', [])
        history.append(f"User: {user_msg}")
        history.append(f"Elina: {diet_reply}")
        request.session['chat_history_list'] = history[-10:]
        return JsonResponse({'reply': diet_reply})

    # 3. Call Groq
    response_data = coach.generate_response(
        user_msg,
        mem.ai_facts,
        history_text,
        site_context,
        language_mode=language_mode,
        auth_line=auth_line,
        profile_context=profile_context,
        rapport_level=prior_turns,
    )

    try:
        # Clean AI response
        raw_content = response_data.strip()
        if raw_content.startswith("```json"):
            raw_content = raw_content.replace("```json", "", 1).replace("```", "", 1).strip()
        elif raw_content.startswith("```"):
            raw_content = raw_content.replace("```", "", 1).replace("```", "", 1).strip()

        def _extract_json_object(text):
            text = (text or "").strip()
            # If it's already JSON, parse directly.
            try:
                return json.loads(text)
            except Exception:
                pass
            # Otherwise, try to extract the first {...} block.
            try:
                start = text.find("{")
                end = text.rfind("}")
                if start != -1 and end != -1 and end > start:
                    return json.loads(text[start:end+1])
            except Exception:
                pass
            # Last resort: pull "reply" field from partial / noisy output
            m = re.search(r'"reply"\s*:\s*"((?:[^"\\]|\\.)*)"', text, flags=re.DOTALL)
            if m:
                inner = m.group(1).replace("\\n", "\n").replace('\\"', '"').replace("\\\\", "\\")
                return {"reply": inner, "new_facts": {}, "search_query": None}
            return None

        ai_json = _extract_json_object(raw_content)
        if not isinstance(ai_json, dict):
            # Handle plain-text model replies gracefully.
            plain = re.sub(r"\{[\s\S]*\}$", "", raw_content).strip()
            reply_text = plain or "Hmph. Say that again in fewer tangled words."

            # Critical fallback: still allow diet-save flow even when model output is not JSON.
            if _wants_to_save_diet_plan(user_msg):
                payload = _extract_diet_payload_from_ai({"reply": reply_text, "new_facts": {}})
                if not payload:
                    strict_prompt = (
                        "Extract a storable daily diet plan from the content below.\n"
                        "Return STRICT JSON ONLY with exactly:\n"
                        '{"title":"...","breakfast":"...","lunch":"...","dinner":"...","calories":2000}\n\n'
                        f"User request:\n{user_msg}\n\n"
                        f"Assistant draft reply:\n{reply_text}\n\n"
                        "Rules: keep each meal concise and practical. If missing info, infer reasonable local-food options."
                    )
                    strict_raw = coach.generate_response(
                        user_msg,
                        mem.ai_facts,
                        history_text,
                        site_context,
                        language_mode=language_mode,
                        auth_line=auth_line,
                        profile_context=profile_context,
                        user_content_override=strict_prompt,
                        rapport_level=prior_turns,
                    )
                    strict_json = _extract_json_object_loose(
                        (strict_raw or "").replace("```json", "").replace("```", "").strip()
                    )
                    if isinstance(strict_json, dict):
                        payload = _extract_diet_payload_from_ai({"new_facts": {"diet_plan": strict_json}})

                if payload:
                    _save_diet_plan_record(payload, mem=mem, request_user=request.user)
                    confirm = (
                        "Diet plan saved to your Diet page."
                        if language_mode == "english"
                        else "Diet plan save kore dilam. Diet page e peye jabe."
                    )
                    reply_text = f"{reply_text} {confirm}".strip()
                else:
                    fallback = (
                        "I could not build a valid breakfast/lunch/dinner plan to save. Ask again with clearer meal sections."
                        if language_mode == "english"
                        else "Valid breakfast/lunch/dinner plan build korte parlam na save er jonno. Aro clear meal section diye abar bolo."
                    )
                    reply_text = f"{reply_text} {fallback}".strip()

            return JsonResponse({"reply": reply_text})
        
        # Handle Internet Search
        if ai_json.get("search_query") and _should_allow_internet_search(user_msg):
            search_info = coach.search_internet(ai_json["search_query"])
            try:
                search_blob = json.dumps(search_info, ensure_ascii=False)
            except Exception:
                search_blob = str(search_info)
            if len(search_blob) > 12000:
                search_blob = search_blob[:12000] + "...(truncated)"
            search_user_content = (
                f"Internet search results for query '{ai_json['search_query']}':\n{search_blob}\n\n"
                f"Recent conversation:\n{history_text}\n\n"
                f"User's original message:\n{user_msg}\n\n"
                "Use the search results when helpful. Answer in the same language mode as the user's message. "
                "Output STRICT JSON as defined in the system instructions."
            )
            response_data = coach.generate_response(
                user_msg,
                mem.ai_facts,
                history_text,
                site_context,
                language_mode=language_mode,
                auth_line=auth_line,
                profile_context=profile_context,
                user_content_override=search_user_content,
                rapport_level=prior_turns,
            )
            cleaned = response_data.strip().replace("```json", "").replace("```", "").strip()
            ai_json = _extract_json_object(cleaned) or {}

        # Update Facts (only for logged-in users with memory)
        if ai_json and ai_json.get("new_facts") and mem:
            mem.ai_facts.update(ai_json["new_facts"])
            mem.save()
        
        # FIXED: Update session history so she remembers next time
        history = request.session.get('chat_history_list', [])
        history.append(f"User: {user_msg}")
        reply_to_store = ai_json.get('reply', '') if ai_json else "Hmph. Brain lag."
        history.append(f"Elina: {reply_to_store}")
        request.session['chat_history_list'] = history[-10:] # Keep last 10 turns
        
        reply_text = ai_json.get('reply', "Hmph. Meow. Ask something useful.") if ai_json else "Hmph. Meow. Ask something useful."
        # If the model hallucinated login status, correct it.
        if request.user.is_authenticated and ("not logged in" in reply_text.lower() or "login first" in reply_text.lower()):
            reply_text = reply_text.replace("login first", "you’re already logged in")
        if _is_profile_related_query(user_msg):
            summary = _profile_usage_summary(request)
            if summary:
                if language_mode == "english":
                    reply_text = f"Fine, I'm peeking at your profile ({summary}). {reply_text}"
                else:
                    reply_text = f"Tch, profile dekhe bolchi ({summary}). {reply_text}"

        # Save diet plan directly from chatbot when user explicitly asks to save/add.
        if _wants_to_save_diet_plan(user_msg):
            payload = _extract_diet_payload_from_ai(ai_json)
            # Fallback: ask AI for a strict diet-plan JSON if meal lines were not parseable.
            if not payload:
                strict_prompt = (
                    "Extract a storable daily diet plan from the content below.\n"
                    "Return STRICT JSON ONLY with exactly:\n"
                    '{"title":"...","breakfast":"...","lunch":"...","dinner":"...","calories":2000}\n\n'
                    f"User request:\n{user_msg}\n\n"
                    f"Assistant draft reply:\n{ai_json.get('reply', '')}\n\n"
                    "Rules: keep each meal concise and practical. If missing info, infer reasonable local-food options."
                )
                strict_raw = coach.generate_response(
                    user_msg,
                    mem.ai_facts,
                    history_text,
                    site_context,
                    language_mode=language_mode,
                    auth_line=auth_line,
                    profile_context=profile_context,
                    user_content_override=strict_prompt,
                    rapport_level=prior_turns,
                )
                strict_json = _extract_json_object_loose(
                    (strict_raw or "").replace("```json", "").replace("```", "").strip()
                )
                if isinstance(strict_json, dict):
                    payload = _extract_diet_payload_from_ai({"new_facts": {"diet_plan": strict_json}})

            if payload:
                _save_diet_plan_record(payload, mem=mem, request_user=request.user)
                confirm = (
                    "Diet plan saved to your Diet page."
                    if language_mode == "english"
                    else "Diet plan save kore dilam. Diet page e peye jabe."
                )
                reply_text = f"{reply_text} {confirm}".strip()
            else:
                fallback = (
                    "I could not detect clear breakfast/lunch/dinner lines to save. Ask me again with those three parts."
                    if language_mode == "english"
                    else "Clear breakfast/lunch/dinner line pelam na save korar jonno. Oi 3ta diye abar bolo."
                )
                reply_text = f"{reply_text} {fallback}".strip()

        return JsonResponse({'reply': reply_text})

    except Exception as e:
        print(f"Error: {e}")
        return JsonResponse({'reply': response_data if response_data else "Tch. Something broke. Try again before I nap."})


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

    # 3. Get current weight from latest progress log if profile weight is not set
    current_weight = getattr(user_profile, 'weight', 0) if user_profile else 0
    if not current_weight:
        latest_log = UserProgress.objects.filter(user=request.user).exclude(current_weight__isnull=True).order_by('-date').first()
        if latest_log and latest_log.current_weight:
            current_weight = float(latest_log.current_weight)

    # 4. Build the context (Indented exactly 4 spaces)
    context = {
        'user_full_name': request.user.get_full_name() or request.user.username,
        'current_weight': current_weight,
        'goal_weight': getattr(user_profile, 'goal_weight', 0) if user_profile else 0,
        'user_height': float(getattr(user_profile, 'height', 0)) if user_profile else 0,
        'daily_bmr': user_profile.calculate_daily_calories() if user_profile and user_profile.weight and user_profile.height and user_profile.age else 0,
        'total_calories': sum(calories),
        'dates_json': json.dumps(dates),
        'calories_json': json.dumps(calories),
        'durations_json': json.dumps(durations),
    }

    # 5. Return the response (Indented exactly 4 spaces)
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
        try:
            data = json.loads(request.body)
            exercise_name = data.get('exercise_name')
            duration_mins = float(data.get('duration', 0))
            
            # 1. Calculate Burn
            try:
                exercise = Exercise.objects.get(name__iexact=exercise_name)
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

            return JsonResponse({'status': 'success', 'burned': calories_burned, 'total_calories': progress.calories_burned})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

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
            scope = str(payload.get("scope", "latest")).lower()
            plan_index = payload.get("index")
            has_user_field = any(field.name == 'user' for field in DietPlan._meta.fields)

            if has_user_field:
                if not request.user.is_authenticated:
                    return JsonResponse({'status': 'error', 'message': 'User not logged in'})
                base_qs = DietPlan.objects.filter(user=request.user)
            else:
                base_qs = DietPlan.objects.all()

            # Stable numbering: Plan #1 = oldest (lowest id), same order as diet page.
            plans_ordered = list(base_qs.order_by("id"))
            total = len(plans_ordered)

            deleted_count = 0

            if scope == "all":
                deleted_count, _ = base_qs.delete()
                message = f"Deleted all {deleted_count} diet plan(s)."
            elif scope == "index":
                try:
                    n = int(plan_index)
                except (TypeError, ValueError):
                    return JsonResponse({
                        'status': 'error',
                        'message': 'Invalid plan number. Send a positive integer (e.g. delete plan 2).',
                    }, status=400)
                if n < 1 or n > total:
                    return JsonResponse({
                        'status': 'error',
                        'message': f'Plan #{n} does not exist. You have {total} saved plan(s) (numbered 1–{total}).',
                    }, status=400)
                plan = plans_ordered[n - 1]
                title = plan.title
                plan.delete()
                deleted_count = 1
                message = f'Deleted plan #{n}: "{title}".'
            elif scope == "latest":
                if not plans_ordered:
                    deleted_count = 0
                else:
                    plan = plans_ordered[-1]
                    title = plan.title
                    plan.delete()
                    deleted_count = 1
                    message = f'Deleted latest plan: "{title}" (was #{total}).'
            else:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Invalid scope. Use "latest", "all", or "index" with a number.',
                }, status=400)

            # Keep AI memory/session aligned after deletion.
            if request.user.is_authenticated:
                mem, _ = MemberMemory.objects.get_or_create(user=request.user)
                facts = mem.ai_facts or {}
                if has_user_field:
                    facts["diet_plan_exists"] = DietPlan.objects.filter(user=request.user).exists()
                else:
                    facts["diet_plan_exists"] = DietPlan.objects.exists()
                mem.ai_facts = facts
                mem.save()
            request.session['chat_history_list'] = []

            if deleted_count > 0:
                return JsonResponse({
                    'status': 'success',
                    'message': message
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


@login_required
def toggle_2fa(request):
    if request.method == "POST":
        from frontend.models import UserTwoFactor
        two_fa, created = UserTwoFactor.objects.get_or_create(user=request.user)
        two_fa.is_enabled = not two_fa.is_enabled
        two_fa.save()
        status = "enabled" if two_fa.is_enabled else "disabled"
        messages.success(request, f"Two-Factor Authentication {status} successfully.")
    return redirect('profile')


def login_view(request):
    from django.contrib.auth import authenticate, login as auth_login
    from django.contrib.auth.models import User
    from frontend.models import UserTwoFactor, LoginOTP
    from django.core.mail import send_mail
    from django.conf import settings
    import random

    if request.user.is_authenticated:
        return redirect('home')

    if request.method == "POST":

        # Step 2 — OTP submitted
        if 'otp' in request.POST:
            user_id = request.session.get('otp_user_id')
            otp_input = request.POST.get('otp')
            if not user_id:
                messages.error(request, "Session expired. Please login again.")
                from django.contrib.auth.forms import AuthenticationForm
                return render(request, 'login.html', {'show_otp': False, 'form': AuthenticationForm()})
            try:
                user = User.objects.get(id=user_id)
                otp_obj = LoginOTP.objects.get(user=user)
                if otp_obj.is_valid() and otp_obj.code == otp_input:
                    otp_obj.delete()
                    del request.session['otp_user_id']
                    auth_login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                    return redirect('home')
                else:
                    return render(request, 'login.html', {
                        'show_otp': True,
                        'error': 'Invalid or expired OTP. Try again.'
                    })
            except Exception:
                messages.error(request, "Something went wrong. Please login again.")
                from django.contrib.auth.forms import AuthenticationForm
                return render(request, 'login.html', {'show_otp': False, 'form': AuthenticationForm()})

        # Step 1 — Email + password submitted
        username_or_email = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()

        # Try username first, then email
        user = authenticate(request, username=username_or_email, password=password)
        if user is None:
            user_obj = User.objects.filter(email__iexact=username_or_email).first()
            if user_obj:
                user = authenticate(request, username=user_obj.username, password=password)

        if user is None:
            return render(request, 'login.html', {'error': 'Invalid email/username or password.'})

        if not user.is_active:
            return render(request, 'login.html', {'error': 'Please verify your email before logging in.'})

        # Check if 2FA is enabled for this user
        try:
            two_fa = UserTwoFactor.objects.get(user=user)
            tfa_enabled = two_fa.is_enabled
        except UserTwoFactor.DoesNotExist:
            tfa_enabled = False

        if tfa_enabled:
            # Generate and send OTP
            code = str(random.randint(100000, 999999))
            LoginOTP.objects.update_or_create(user=user, defaults={'code': code})
            send_mail(
                '🔐 Your Login Code - M-Power Fitness',
                f'''Hello {user.username},

Your login verification code is:

{code}

This code expires in 5 minutes.

If you did not attempt to login, please change your password immediately.

— M-Power Fitness Security Team''',
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
            )
            request.session['otp_user_id'] = user.id
            return render(request, 'login.html', {
                'show_otp': True,
                'email': user.email
            })

        # No 2FA — log in directly
        auth_login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        return redirect('home')

    from django.contrib.auth.forms import AuthenticationForm
    form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})