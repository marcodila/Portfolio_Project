from django.contrib import admin
from .models import Project, ProjectFile


class ProjectFileInline(admin.TabularInline):
    model = ProjectFile
    extra = 1
    fields = ('label', 'file', 'order')


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'is_featured', 'order', 'created_at')
    list_filter = ('category', 'is_featured')
    list_editable = ('is_featured', 'order')
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ('title', 'one_sentence_summary')
    inlines = [ProjectFileInline]
    fieldsets = (
        (None, {'fields': ('title', 'slug', 'category', 'one_sentence_summary', 'order', 'is_featured')}),
        ('Content', {'fields': ('business_problem', 'tools_used', 'key_features', 'role_and_contribution', 'biggest_challenge', 'what_i_learned')}),
        ('Media & Links', {'fields': ('image', 'github_url', 'demo_url')}),
    )


@admin.register(ProjectFile)
class ProjectFileAdmin(admin.ModelAdmin):
    list_display = ('label', 'project', 'extension', 'order')
    list_filter = ('project',)

    def extension(self, obj):
        return obj.extension
    extension.short_description = 'Type'
