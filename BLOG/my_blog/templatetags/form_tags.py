from django import template

register = template.Library()

@register.filter(name='add_class')
def add_class(field, css):
    """Ajoute une classe CSS à un champ Django Form"""
    return field.as_widget(attrs={"class": css})
