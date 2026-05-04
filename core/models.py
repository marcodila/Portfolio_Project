from django.db import models


class Skill(models.Model):
    CATEGORY_CHOICES = [
        ('languages', 'Languages & Frameworks'),
        ('ai_ml', 'AI / ML Tools'),
        ('data', 'Data & Analytics'),
        ('cloud', 'Cloud & DevOps'),
        ('business', 'Business & Finance'),
    ]

    name = models.CharField(max_length=100)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    proficiency = models.IntegerField(default=80)  # 0–100 for progress bar rendering
    icon_class = models.CharField(max_length=50, blank=True)  # Bootstrap Icons class
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['category', 'order']

    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"


class ContactMessage(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField()
    subject = models.CharField(max_length=300)
    message = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-submitted_at']

    def __str__(self):
        return f"{self.name} — {self.subject}"
