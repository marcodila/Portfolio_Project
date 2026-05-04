from django.views.generic import TemplateView, FormView
from django.urls import reverse_lazy
from django.contrib import messages

from projects.models import Project
from .models import Skill
from .forms import ContactForm


class HomeView(TemplateView):
    template_name = 'core/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['featured_projects'] = Project.objects.filter(is_featured=True)[:3]
        # Grab a flat list of AI/ML skills for the quick-tools section on home
        context['ai_skills'] = Skill.objects.filter(category='ai_ml')[:8]
        return context


class AboutView(TemplateView):
    template_name = 'core/about.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['interests'] = [
            'Golf', 'Macro Economics', 'Music Festivals',
            'Investing', 'AI Research', 'Financial Markets',
        ]
        return context


class SkillsView(TemplateView):
    template_name = 'core/skills.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Group skills by category for template iteration
        skills = Skill.objects.all()
        grouped: dict[str, list] = {}
        for skill in skills:
            grouped.setdefault(skill.get_category_display(), []).append(skill)
        context['grouped_skills'] = grouped
        return context


class ResumeView(TemplateView):
    template_name = 'core/resume.html'


class ContactView(FormView):
    template_name = 'core/contact.html'
    form_class = ContactForm
    success_url = reverse_lazy('core:contact')

    def form_valid(self, form):
        form.save()
        messages.success(
            self.request,
            "Thanks for reaching out! I'll get back to you soon."
        )
        return super().form_valid(form)
