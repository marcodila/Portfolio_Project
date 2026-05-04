from django.db import models
from django.urls import reverse


class Project(models.Model):
    CATEGORY_CHOICES = [
        ('chatbot', 'Chatbot'),
        ('workflow', 'Agent Workflow'),
        ('langchain', 'LangChain Agent'),
        ('media', 'AI Media'),
        ('ml', 'Machine Learning'),
        ('web', 'Web Application'),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    one_sentence_summary = models.CharField(max_length=300)
    business_problem = models.TextField()
    tools_used = models.JSONField(default=list)     # e.g. ["Python", "LangChain", "FAISS"]
    key_features = models.JSONField(default=list)   # bullet strings
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
