from django.views.generic import TemplateView


class HomeView(TemplateView):
    template_name = "core/home.html"


class WorkInProgressView(TemplateView):
    template_name = "core/work_in_progress.html"
