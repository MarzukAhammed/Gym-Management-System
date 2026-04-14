from django.contrib import admin
from django.contrib.auth.models import Group
from django.utils.html import format_html
from django.urls import reverse
from .models import Plan, Trainer, Member, Review, Contact, GalleryMember, SuccessStory, Payment, TrainingSession, Notification, TrainingSlot
from .forms import TrainerCreateForm

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
    list_display = ('name', 'specialty', 'delete_button') # ID bad diye 'name'
    search_fields = ('name', 'specialty') # Protita section-e search bar
    add_form = TrainerCreateForm

    def get_form(self, request, obj=None, **kwargs):
        defaults = {}
        if obj is None:
            defaults["form"] = self.add_form
        defaults.update(kwargs)
        return super().get_form(request, obj, **defaults)

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
        updated = queryset.update(verified=True)
        self.message_user(request, f"{updated} payment(s) marked as received.")
    mark_payment_received.short_description = "Mark selected payments as received"

@admin.register(Review)
class ReviewAdmin(ActionAdmin):
    list_display = ("user", "rating", "delete_button")
    search_fields = ("user__username", "comment")

@admin.register(GalleryMember)
class GalleryMemberAdmin(ActionAdmin):
    list_display = ('id', 'delete_button') 
    search_fields = ('id',) # image_9f8ccb fix

@admin.register(Contact)
class ContactAdmin(ActionAdmin):
    # Subject field-e error chilo tai ota bad deya holo
    list_display = ('name', 'email', 'delete_button') 
    search_fields = ('name', 'email')

@admin.register(SuccessStory)
class SuccessStoryAdmin(ActionAdmin):
    list_display = ('title', 'delete_button')
    search_fields = ('title',)


@admin.register(TrainingSession)
class TrainingSessionAdmin(ActionAdmin):
    list_display = ("trainer", "user", "session_time", "is_active", "delete_button")
    search_fields = ("trainer__name", "user__username", "meeting_link")
    list_filter = ("is_active", "trainer")


@admin.register(TrainingSlot)
class TrainingSlotAdmin(ActionAdmin):
    list_display = ("trainer", "session_time", "is_active", "is_booked", "booked_by", "delete_button")
    search_fields = ("trainer__name", "meeting_link", "booked_by__username")
    list_filter = ("is_active", "is_booked", "trainer")


@admin.register(Notification)
class NotificationAdmin(ActionAdmin):
    list_display = ("user", "level", "is_read", "created_at", "delete_button")
    search_fields = ("user__username", "text")
    list_filter = ("level", "is_read")