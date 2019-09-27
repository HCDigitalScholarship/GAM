from django import template
register = template.Library()

@register.filter(name='filters')
def filters(value):
    filters = value.filters_list()
    return filters
