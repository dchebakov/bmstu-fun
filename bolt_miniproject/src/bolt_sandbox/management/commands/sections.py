from django.core.management.base import BaseCommand, CommandError
from bolt_sandbox.models import Section

sections = [('Мои задачи', 'solutions')]


def create_section():
    for title, slug in sections:
        Section.objects.create(title=title, slug=slug)


class Command(BaseCommand):
    def handle(self, *args, **options):
        create_section()
