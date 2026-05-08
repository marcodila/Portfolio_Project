from django import forms
from django.contrib import admin
from .models import Project, ProjectFile

_JSON_HELP = (
    'Enter as a JSON array of strings. Example: '
    '["Item one", "Item two", "Item three"]. '
    'Use double quotes only — no trailing comma after the last item.'
)


class ProjectAdminForm(forms.ModelForm):
    """Custom form that gives tools_used and key_features a tall textarea."""

    tools_used = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4, 'style': 'font-family: monospace; font-size: 13px;'}),
        help_text='One tool per line is fine — or paste the full JSON array. Example:<br>'
                  '<code>["Python", "Django", "LangChain", "FAISS"]</code>',
        initial='[]',
    )
    key_features = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 8, 'style': 'font-family: monospace; font-size: 13px;'}),
        help_text='Each bullet point as a quoted string in a JSON array. Example:<br>'
                  '<code>["Built RAG pipeline with FAISS", "AJAX chat interface", "Session rate limiting"]</code>',
        initial='[]',
    )

    class Meta:
        model = Project
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        import json
        # Pre-populate with pretty-printed JSON so the textarea looks clean on edit
        for field in ('tools_used', 'key_features'):
            value = getattr(self.instance, field, None)
            if value is not None:
                self.fields[field].initial = json.dumps(value, indent=2)
                if self.instance.pk:
                    self.initial[field] = json.dumps(value, indent=2)

    def clean_tools_used(self):
        return self._parse_json_list('tools_used')

    def clean_key_features(self):
        return self._parse_json_list('key_features')

    def _parse_json_list(self, field_name):
        import json
        raw = self.cleaned_data.get(field_name, '').strip()
        # Accept bare comma-separated values as a convenience (no brackets needed)
        if raw and not raw.startswith('['):
            items = [s.strip().strip('"').strip("'") for s in raw.split(',') if s.strip()]
            return items
        try:
            parsed = json.loads(raw or '[]')
        except json.JSONDecodeError as e:
            raise forms.ValidationError(
                f'Invalid JSON — {e}. Wrap items in ["double quotes"] inside square brackets.'
            )
        if not isinstance(parsed, list):
            raise forms.ValidationError('Must be a JSON array (starts and ends with [ ]).')
        return parsed


class ProjectFileInline(admin.TabularInline):
    model = ProjectFile
    extra = 1
    fields = ('label', 'file', 'order')


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    form = ProjectAdminForm
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
