from django.contrib import admin
from .models import Plan, Trainer, Member
from .models import Contact

admin.site.register(Plan)
admin.site.register(Trainer)
admin.site.register(Member)
admin.site.register(Contact)
