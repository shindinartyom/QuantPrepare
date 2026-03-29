from django.contrib import admin
from .models import Problem, Attempt

@admin.register(Problem)
class ProblemAdmin(admin.ModelAdmin):
    list_display = ['title', 'difficulty', 'correct_answer', 'created_at']
    list_filter = ['difficulty', 'created_at']
    search_fields = ['title', 'description']

@admin.register(Attempt)
class AttemptAdmin(admin.ModelAdmin):
    list_display = ['problem', 'user_answer', 'is_correct', 'timestamp']
    list_filter = ['is_correct', 'timestamp']
    search_fields = ['problem__title']