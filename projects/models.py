import os
from django.db import models
from django.urls import reverse


class Project(models.Model):
    CATEGORY_CHOICES = [
        # AI / Engineering
        ('chatbot', 'Chatbot'),
        ('workflow', 'Agent Workflow'),
        ('langchain', 'LangChain Agent'),
        ('media', 'AI Media'),
        ('ml', 'Machine Learning'),
        ('web', 'Web Application'),
        ('quant', 'Quant Finance'),
        # Finance & Business
        ('equity_research', 'Equity Research'),
        ('dashboard', 'Dashboard'),
        ('financial_model', 'Financial Model'),
        ('case_competition', 'Case Competition'),
        ('hackathon', 'Hackathon'),
        ('presentation', 'Presentation'),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    one_sentence_summary = models.CharField(max_length=300)
    business_problem = models.TextField()
    tools_used = models.JSONField(default=list)
    key_features = models.JSONField(default=list)
    role_and_contribution = models.TextField()
    biggest_challenge = models.TextField()
    what_i_learned = models.TextField()
    image = models.ImageField(upload_to='projects/', blank=True, null=True)
    github_url = models.URLField(blank=True)
    demo_url = models.URLField(blank=True)
    order = models.PositiveIntegerField(default=0)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'title']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('projects:detail', kwargs={'slug': self.slug})

    @property
    def static_image_name(self):
        """Filename only, for WhiteNoise static fallback in templates."""
        if self.image:
            return os.path.basename(self.image.name)
        return None


class ProjectFile(models.Model):
    """
    Arbitrary file attachment for a project — PDF decks, Excel models,
    PowerPoint presentations, CSV data, etc.
    Multiple files can be attached to a single project via the admin inline.
    """
    FILE_TYPE_ICONS = {
        '.pdf':  'bi-file-earmark-pdf',
        '.xlsx': 'bi-file-earmark-spreadsheet',
        '.xls':  'bi-file-earmark-spreadsheet',
        '.pptx': 'bi-file-earmark-slides',
        '.ppt':  'bi-file-earmark-slides',
        '.docx': 'bi-file-earmark-word',
        '.doc':  'bi-file-earmark-word',
        '.csv':  'bi-file-earmark-bar-graph',
        '.zip':  'bi-file-earmark-zip',
    }

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='files')
    label = models.CharField(max_length=100, help_text='Button label, e.g. "Download Deck" or "View Model"')
    file = models.FileField(upload_to='project_files/')

    def save(self, *args, **kwargs):
        # Ensure the upload directory exists before the file system write
        from django.conf import settings
        upload_dir = settings.MEDIA_ROOT / 'project_files'
        upload_dir.mkdir(parents=True, exist_ok=True)
        super().save(*args, **kwargs)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'label']

    def __str__(self):
        return f"{self.project.title} — {self.label}"

    @property
    def icon_class(self) -> str:
        """Bootstrap Icons class based on file extension."""
        ext = os.path.splitext(self.file.name)[1].lower()
        return self.FILE_TYPE_ICONS.get(ext, 'bi-file-earmark')

    @property
    def extension(self) -> str:
        return os.path.splitext(self.file.name)[1].lstrip('.').upper()
