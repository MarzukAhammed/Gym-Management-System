from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Plan, Trainer, Member, Review, Contact, GalleryMember, SuccessStory, DietPlan, Payment

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

@admin.register(Plan)
class PlanAdmin(ActionAdmin):
    list_display = ('title', 'price', 'delete_button')
    search_fields = ('title',)

@admin.register(Member)
class MemberAdmin(ActionAdmin):
    list_display = ('user', 'plan', 'delete_button') 
    search_fields = ('user__username', 'plan__title')

@admin.register(DietPlan)
class DietPlanAdmin(ActionAdmin):
    list_display = ('title', 'calories', 'delete_button')
    search_fields = ('title',)

@admin.register(Payment)
class PaymentAdmin(ActionAdmin):
    list_display = ('full_name', 'amount', 'verified', 'delete_button')
    search_fields = ('full_name', 'phone', 'transaction_id')

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