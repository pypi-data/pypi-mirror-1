from django.template import Library
from django.contrib.admin.templatetags.admin_list import items_for_result, result_headers

register = Library()

def results(cl):
    for res in cl.result_list:
        yield {'id': res.id,
               'items': list(items_for_result(cl,res)),
              }


@register.inclusion_tag('admin/change_list_results.html')
def emencia_result_list(cl):
    return {'cl': cl,
            'result_headers': list(result_headers(cl)),
            'type': cl.model.__name__.lower(),
            'results': list(results(cl))}

