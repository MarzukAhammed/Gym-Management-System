from django.contrib import admin
from django.contrib.auth.models import Group
from django.utils.html import format_html
from django.urls import reverse
from .models import Plan, Trainer, Member, Review, TrainerReview, Contact, GalleryMember, SuccessStory, Payment, TrainingSession, Notification, TrainingSlot, DailyChallenge, ChallengeSubmission, UserChallengeProfile, ChallengeVideoComment
from .forms import TrainerCreateForm, TrainerAdminForm

admin.site.unregister(Group)

# ১. BaseAdmin (Buttons hide + Action bar remove)
class BaseAdmin(admin.ModelAdmin):
    actions = None # image_9f8920 check: Action dropdown remove korbe
    
    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        context.update({
            'show_save_and_add_another': False,
            'show_save_and_continue': False,
        })
        return super().render_change_form(request, context, add, change, form_url, obj)

# ২. ActionAdmin (Delete button + Common Search Logic)
class ActionAdmin(BaseAdmin): 
    def delete_button(self, obj):
        opts = obj._meta
        delete_url = reverse(f'admin:{opts.app_label}_{opts.model_name}_delete', args=[obj.pk])
        return format_html(
            '<a class="deletelink" href="{}" style="color: #ff4444; font-weight: bold; text-decoration: none;">× Delete</a>',
            delete_url
        )
    delete_button.short_description = "Action"

# ৩. Global CSS for clean UI
admin.ModelAdmin.Media = type('Media', (), {
    'css': {'all': ('data:text/css,.submit-row input[name="_addanother"], .submit-row input[name="_continue"] { display: none !important; }',)}
})

# ৪. Protita Section-er jonno Specific Admin (Search + Name fix)

@admin.register(Trainer)
class TrainerAdmin(ActionAdmin):
    list_display = ('name', 'specialty', 'get_email', 'delete_button') # ID bad diye 'name'
    search_fields = ('name', 'specialty', 'user__email') # Protita section-e search bar
    form = TrainerAdminForm

    def get_email(self, obj):
        return obj.user.email if obj.user else "No Email"
    get_email.short_description = 'Email'

@admin.register(Plan)
class PlanAdmin(ActionAdmin):
    list_display = ('title', 'price', 'delete_button')
    search_fields = ('title',)

@admin.register(Member)
class MemberAdmin(ActionAdmin):
    list_display = ('user', 'plan', 'delete_button') 
    search_fields = ('user__username', 'plan__title')

@admin.register(Payment)
class PaymentAdmin(ActionAdmin):
    list_display = ('full_name', 'amount', 'verified', 'mark_received_button', 'delete_button')
    search_fields = ('full_name', 'phone', 'transaction_id')
    actions = ['mark_payment_received']

    def mark_received_button(self, obj):
        if obj.verified:
            return format_html('<span style="color:#22c55e;font-weight:700;">Received</span>')
        return format_html('<span style="color:#f59e0b;font-weight:700;">Pending</span>')
    mark_received_button.short_description = "Payment Received"

    def mark_payment_received(self, request, queryset):
        from .models import Notification
        updated = 0
        for payment in queryset.filter(verified=False):
            payment.verified = True
            payment.save(update_fields=['verified'])
            updated += 1
            if payment.user:
                Notification.objects.create(
                    user=payment.user,
                    level="success",
                    text=f"✅ Your payment of {payment.amount} BDT has been verified. Welcome to our gym!",
                    is_read=False,
                )
        self.message_user(request, f"{updated} payment(s) marked as received and users notified.")
    mark_payment_received.short_description = "Mark selected payments as received"

    def save_model(self, request, obj, form, change):
        from .models import Notification
        
        # Check if verified status is changing from False to True
        if change:
            old_obj = Payment.objects.filter(pk=obj.pk).first()
            if old_obj and not old_obj.verified and obj.verified:
                if obj.user:
                    Notification.objects.create(
                        user=obj.user,
                        level="success",
                        text=f"✅ Your payment of {obj.amount} BDT has been verified. Welcome to our gym!",
                        is_read=False,
                    )
        
        super().save_model(request, obj, form, change)

@admin.register(GalleryMember)
class GalleryMemberAdmin(ActionAdmin):
    list_display = ('id', 'delete_button') 
    search_fields = ('id',) # image_9f8ccb fix

@admin.register(Contact)
class ContactAdmin(ActionAdmin):
    # Subject field-e error chilo tai ota bad deya holo
    list_display = ('name', 'email', 'delete_button') 
    search_fields = ('name', 'email')

@admin.register(DailyChallenge)
class DailyChallengeAdmin(ActionAdmin):
    list_display = ("title", "day_of_week", "coins_reward", "is_active", "delete_button")
    search_fields = ("title", "instruction")
    list_filter = ("day_of_week", "is_active")


@admin.register(ChallengeSubmission)
class ChallengeSubmissionAdmin(ActionAdmin):
    list_display = ("challenge", "user", "coins_granted", "coins_approved", "created_at", "approve_button", "delete_button")
    search_fields = ("challenge__title", "user__username")
    list_filter = ("challenge", "coins_approved")
    actions = ["approve_selected_coins", "revoke_selected_coins"]

    def approve_button(self, obj):
        if obj.coins_approved or obj.coins_granted <= 0:
            return format_html('<span style="color:#22c55e;font-weight:700;">Approved</span>')
        return format_html('<span style="color:#f59e0b;font-weight:700;">Pending</span>')
    approve_button.short_description = "Coins"

    def approve_selected_coins(self, request, queryset):
        from django.utils import timezone
        from .models import Profile, Notification, UserChallengeProfile

        approved_count = 0
        for sub in queryset.select_related("user", "challenge"):
            if sub.coins_granted <= 0 or sub.coins_approved:
                continue
            sub.coins_approved = True
            sub.coins_approved_at = timezone.now()
            sub.save(update_fields=["coins_approved", "coins_approved_at"])

            # Add to main Profile coins
            prof, _ = Profile.objects.get_or_create(user=sub.user)
            prof.gym_coins = int(getattr(prof, "gym_coins", 0) or 0) + int(sub.coins_granted)
            prof.save(update_fields=["gym_coins"])

            # Keep challenge-profile coins in sync too
            cp, _ = UserChallengeProfile.objects.get_or_create(user=sub.user)
            cp.gym_coins = int(getattr(cp, "gym_coins", 0) or 0) + int(sub.coins_granted)
            cp.save(update_fields=["gym_coins"])

            Notification.objects.create(
                user=sub.user,
                level="success",
                text=f"✅ Coins approved: +{sub.coins_granted} Gym Coins for '{sub.challenge.title}'.",
                is_read=False,
            )
            approved_count += 1

        self.message_user(request, f"{approved_count} submission(s) approved and coins granted.")
    approve_selected_coins.short_description = "Approve coins for selected submissions"

    def revoke_selected_coins(self, request, queryset):
        from .models import Profile, UserChallengeProfile
        revoked_count = 0
        for sub in queryset.select_related("user"):
            if not sub.coins_approved or sub.coins_granted <= 0:
                continue
            # Revoke coins (best-effort; don't go below 0)
            prof, _ = Profile.objects.get_or_create(user=sub.user)
            prof.gym_coins = max(0, int(getattr(prof, "gym_coins", 0) or 0) - int(sub.coins_granted))
            prof.save(update_fields=["gym_coins"])
            cp = UserChallengeProfile.objects.filter(user=sub.user).first()
            if cp:
                cp.gym_coins = max(0, int(getattr(cp, "gym_coins", 0) or 0) - int(sub.coins_granted))
                cp.save(update_fields=["gym_coins"])

            sub.coins_approved = False
            sub.coins_approved_at = None
            sub.save(update_fields=["coins_approved", "coins_approved_at"])
            revoked_count += 1

        self.message_user(request, f"{revoked_count} submission(s) revoked.")
    revoke_selected_coins.short_description = "Revoke coins for selected submissions"

    def save_model(self, request, obj, form, change):
        """
        If an admin manually toggles coins_approved in the change form,
        make sure we grant/revoke coins + notification automatically.
        """
        from django.utils import timezone
        from .models import Profile, Notification, UserChallengeProfile

        prev = None
        if change and obj.pk:
            prev = ChallengeSubmission.objects.filter(pk=obj.pk).first()

        super().save_model(request, obj, form, change)

        if not prev:
            return

        # Approve transition
        if (not prev.coins_approved) and obj.coins_approved and obj.coins_granted > 0:
            if not obj.coins_approved_at:
                obj.coins_approved_at = timezone.now()
                obj.save(update_fields=["coins_approved_at"])

            prof, _ = Profile.objects.get_or_create(user=obj.user)
            prof.gym_coins = int(getattr(prof, "gym_coins", 0) or 0) + int(obj.coins_granted)
            prof.save(update_fields=["gym_coins"])

            cp, _ = UserChallengeProfile.objects.get_or_create(user=obj.user)
            cp.gym_coins = int(getattr(cp, "gym_coins", 0) or 0) + int(obj.coins_granted)
            cp.save(update_fields=["gym_coins"])

            Notification.objects.create(
                user=obj.user,
                level="success",
                text=f"✅ Coins approved: +{obj.coins_granted} Gym Coins for '{obj.challenge.title}'.",
                is_read=False,
            )
            return

        # Revoke transition
        if prev.coins_approved and (not obj.coins_approved) and prev.coins_granted > 0:
            prof, _ = Profile.objects.get_or_create(user=obj.user)
            prof.gym_coins = max(0, int(getattr(prof, "gym_coins", 0) or 0) - int(prev.coins_granted))
            prof.save(update_fields=["gym_coins"])

            cp = UserChallengeProfile.objects.filter(user=obj.user).first()
            if cp:
                cp.gym_coins = max(0, int(getattr(cp, "gym_coins", 0) or 0) - int(prev.coins_granted))
                cp.save(update_fields=["gym_coins"])

            obj.coins_approved_at = None
            obj.save(update_fields=["coins_approved_at"])
