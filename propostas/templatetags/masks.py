from django import template

register = template.Library()

@register.filter
def mask_cpf(value):
    """Aplica máscara de CPF no formato 000.000.000-00"""
    if value and len(value) == 11:
        return f"{value[:3]}.{value[3:6]}.{value[6:9]}-{value[9:]}"
    return value

@register.filter
def mask_cep(value):
    """Aplica máscara de CEP no formato 00000-000"""
    if value and len(value) == 8:
        return f"{value[:5]}-{value[5:]}"
    return value

@register.filter
def mask_phone(value):
    """Aplica máscara de telefone no formato (00) 0000-0000 ou (00) 00000-0000"""
    if value and len(value) == 10:
        return f"({value[:2]}) {value[2:6]}-{value[6:]}"
    elif value and len(value) == 11:
        return f"({value[:2]}) {value[2:7]}-{value[7:]}"
    return value

@register.filter
def mask_currency(value):
    """Aplica formatação de moeda no formato 0.000,00"""
    try:
        return f"{float(value):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except (ValueError, TypeError):
        return value
