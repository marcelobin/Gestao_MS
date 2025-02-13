# propostas_filters.py

from django import template
from decimal import Decimal, InvalidOperation

register = template.Library()

@register.filter
def mul(value, arg):
    """Multiplica dois valores no template, garantindo conversão segura"""
    try:
        value = Decimal(str(value))  # Converte primeiro para string para evitar erros
        arg = Decimal(str(arg))
        return value * arg
    except (ValueError, TypeError, InvalidOperation):
        return Decimal("0.00")  # Retorna 0.00 em caso de erro para evitar falhas no template
