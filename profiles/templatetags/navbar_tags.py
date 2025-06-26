from django import template
from django.urls import resolve, Resolver404

register = template.Library()

@register.simple_tag(takes_context=True)
def should_show_navbar(context):
    try:
        resolver_match = resolve(context['request'].path)
        # Check if we're on the profile form page
        if resolver_match.url_name in ['create_profile', 'edit_profile']:
            return False
    except (KeyError, Resolver404):
        pass
    return True
