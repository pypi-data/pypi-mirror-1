from django.template import Library

register = Library()

@register.inclusion_tag('admin/filter_select.html')
def admin_list_filter_selector(cl, spec):
    choices = []
    for choice in spec.choices(cl):
        query = choice['query_string']
        query = query[1:]
        choice['query_string'] = query
        choices.append(choice)
    return {'title': spec.title(), 'choices' : choices}
