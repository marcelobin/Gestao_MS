from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Retorna o item do dicionário correspondente à chave."""
    try:
        return dictionary[key]
    except (KeyError, TypeError):
        return ''
