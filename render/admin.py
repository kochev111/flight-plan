from django.contrib import admin
from .classes import Plan
# Register your models here.

class planAdmin(admin.ModelAdmin):
    list_display = ["final", "base", "downwind", "initial", "drop", "vertical_speed", "glide_ratio",\
        "swoop", "landing_dir", "pattern_dir", "comment", "pattern"]

admin.site.register(Plan, planAdmin)