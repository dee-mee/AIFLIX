from django.core.management.base import BaseCommand
from django.urls import get_resolver

class Command(BaseCommand):
    help = 'Show all URLs in the project'

    def handle(self, *args, **options):
        resolver = get_resolver()
        self.print_urls(resolver)

    def print_urls(self, urls, parent=''):
        for url in urls.url_patterns:
            if hasattr(url, 'url_patterns'):
                # This is an include
                self.print_urls(url, parent + str(url.pattern))
            else:
                # This is a URL pattern
                self.stdout.write(f"{parent + str(url.pattern)} -> {url.name or 'N/A'}")
                if hasattr(url, 'callback') and hasattr(url.callback, '__name__'):
                    self.stdout.write(f"    View: {url.callback.__module__}.{url.callback.__name__}")
