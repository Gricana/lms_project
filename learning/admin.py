from django.contrib import admin
from .models import Course, Lesson, Review, Tracking


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'start_date', 'description', )
    filter_horizontal = ('authors',)
    list_display_links = ('title', 'start_date', )
    list_editable = ('description', )
    search_fields = ('^title', )
    list_per_page = 3
    actions_on_top = True
    actions_on_bottom = True
    actions_selection_counter = True
    save_on_top = True


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('course', 'name', 'preview', )
    search_fields = ('name', )
    list_per_page = 3
    actions_on_top = False
    actions_on_bottom = True
    actions_selection_counter = True


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'content')
    search_fields = ('content', )
    list_per_page = 100


admin.register(Tracking)
