from django import template
from django.urls import resolve, reverse

register = template.Library()

@register.simple_tag(takes_context=True)
def active_link(context, view_name, *args, **kwargs):
    """
    Returns 'active' if the current URL matches the given view name and namespace.
    Usage: {% active_link 'app_name:view_name' %}
    """
    request = context.get('request')
    if not request:
        return ''
    
    # Get the current URL name and namespace
    try:
        current_url = resolve(request.path_info)
        current_url_name = current_url.url_name
        current_namespace = current_url.namespace
        
        # Get the target URL name and namespace
        target_url = resolve(reverse(view_name, args=args, kwargs=kwargs))
        target_url_name = target_url.url_name
        target_namespace = target_url.namespace
        
        # Check if both URL name and namespace match
        if current_url_name == target_url_name and current_namespace == target_namespace:
            return 'active'
            
    except Exception as e:
        print(f"Error in active_link: {e}")
        pass
        
    return ''
