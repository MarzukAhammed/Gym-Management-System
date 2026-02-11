from django.contrib import admin
from .models import Plan, Trainer, Member, Review
from .models import Contact, GalleryMember
from .models import SuccessStory, DietPlan, Payment

class PlanAdmin(admin.ModelAdmin):
    list_display = ('title', 'price_with_currency')

    def price_with_currency(self, obj):
        return f"{obj.price} ৳"
    price_with_currency.short_description = "Price"

admin.site.register(Plan, PlanAdmin)
admin.site.register(Trainer)
admin.site.register(Member)
admin.site.register(Contact)
admin.site.register(SuccessStory)
admin.site.register(GalleryMember)

@admin.register(DietPlan)
class DietPlanAdmin(admin.ModelAdmin):
    list_display = ('title', 'calories')

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        'full_name',
        'phone',
        'amount',
        'method',
        'transaction_id',
        'verified',
        'created_at',
    )

    list_filter = ('method', 'verified', 'created_at')
    search_fields = ('full_name', 'phone', 'transaction_id')

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("user", "rating", "created_at")
    list_filter = ("rating", "created_at")
    search_fields = ("comment", "user__username")
    ordering = ("-created_at",)
