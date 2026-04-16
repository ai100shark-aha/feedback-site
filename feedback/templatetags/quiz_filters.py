from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """딕셔너리에서 키로 값 조회: {{ my_dict|get_item:key }}"""
    if isinstance(dictionary, dict):
        return dictionary.get(key)
    return None

@register.filter
def sub(value, arg):
    """뺄셈 필터: {{ value|sub:arg }}"""
    try:
        return int(value) - int(arg)
    except (TypeError, ValueError):
        return value
