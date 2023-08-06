from django.contrib import admin
from django.contrib.admin.views.main import ChangeList
from django.contrib.admin.views import main
from django.db import models
from django.db import transaction
from django.contrib.admin.options import IncorrectLookupParameters
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.utils.translation import ugettext as _
from django import forms
from django.shortcuts import render_to_response
from django.template import RequestContext

import copy
import csv
import cStringIO

def delete(request, app_label, model_name):

    model = models.get_model(app_label, model_name)
    opts = model._meta
    if model is None:
        raise Http404("App %r, model %r, not found" % (app_label, model_name))
    try:
        admin_obj = admin.site._registry[model]
    except KeyError:
        raise http.Http404("This model exists but has not been registered with the admin site.")

    if not request.user.has_perm(app_label + '.' + model._meta.get_change_permission()):
        raise PermissionDenied
    try:
        cl = ChangeList(request, admin_obj.model, admin_obj.list_display,
                        admin_obj.list_display_links, admin_obj.list_filter,
                        admin_obj.date_hierarchy, admin_obj.search_fields,
                        admin_obj.list_select_related,
                        admin_obj.list_per_page, admin_obj)
    except IncorrectLookupParameters:
        # Wacky lookup parameters were given, so redirect to the main
        # changelist page, without parameters, and pass an 'invalid=1'
        # parameter via the query string. If wacky parameters were given and
        # the 'invalid=1' parameter was already in the query string, something
        # is screwed up with the database, so display an error page.
        if ERROR_FLAG in request.GET.keys():
            return render_to_response('admin/invalid_setup.html', {'title': _('Database error')})
        return HttpResponseRedirect(request.path + '?' + ERROR_FLAG + '=1')

    if 'delete_selected' in request.POST and model_name in request.POST:
        deleted = []
        for obj in cl.get_query_set().filter(id__in=request.POST.getlist(model_name)):
            obj.delete()
            deleted.append('"%s"' % str(obj))
        request.user.message_set.create(message=_('The %(name)s %(obj)s were deleted successfully.') % {'name': opts.verbose_name_plural, 'obj': ", ".join(deleted)})

    if 'delete_shown' in request.POST and 'qs_obj' in request.POST:
        deleted = []
        for obj in cl.get_query_set().filter(id__in=request.POST.getlist('qs_obj')):
            obj.delete()
            deleted.append('"%s"' % str(obj))
        request.user.message_set.create(message=_('The %(name)s %(obj)s were deleted successfully.') % {'name': opts.verbose_name_plural, 'obj': ", ".join(deleted)})

    if 'delete_all' in request.POST and cl.get_query_set().count() > 0:
        for obj in cl.get_query_set():
            obj.delete()
        request.user.message_set.create(message=_('All %(name)s were deleted successfully.') % {'name': opts.verbose_name_plural})

    return HttpResponseRedirect('..')


class CSVForm(forms.Form):
    delimiter = forms.ChoiceField(choices = [(';', ';'),
                                             (',', ','),
                                             ('|', '|')])
    encoding = forms.ChoiceField(choices = [('cp1252', 'Windows'),
                                            ('mac_roman', 'Mac'),
                                            ('latin1', 'Latin1'),
                                            ('utf8', 'UTF-8') ])
    import_mode = forms.ChoiceField(choices = [('change', _('Add or replace')),
                                               ('add', _('Add or pass')),
                                               ('test', _('Test')),
                                               ('delete', _('Delete'))],
                                     widget = forms.RadioSelect)
    skip_first = forms.BooleanField()




def csv_form(request, app_label, model_name):
    "CSV Import/Export function"
    model = models.get_model(app_label, model_name)
    if model is None:
        raise Http404("App %r, model %r, not found" % (app_label, model_name))
    opts = model._meta
    try:
        admin_obj = admin.site._registry[model]
    except KeyError:
        raise http.Http404("This model exists but has not been registered with the admin site.")

    if not request.user.has_perm(app_label + '.' + model._meta.get_change_permission()):
        raise PermissionDenied

    field_sets = admin_obj.opts.fields
    fields = []
    for field in field_sets:
        if not request.POST or request.POST.has_key(field.name):
            field = copy.copy(field)
            field.checked = 'checked'
        fields.append(field)

    output = []
    if request.POST:
        form = CSVForm(request.POST)
        encoding = request.POST['encoding']
        action = request.POST['action']
        import_mode = request.POST['import_mode']
        delimiter = request.POST['delimiter']
        skip_first = request.POST.get('skip_first', False)
    else:
        form = CSVForm(initial = { 'delimiter' : ':',
                                   'encoding' : 'latin1',
                                   'import_mode' : 'change',
                                   'skip_first' : True})

    input = []
    if request.FILES:
        csv_data = request.FILES['csv']['content']
        if csv_data.find('\r\n') == -1 and csv_data.find('\r') != -1:
            csv_data = csv_data.replace('\r', '\n') # mac2unix
        output, input = csv_import(csv_data, encoding, delimiter, import_mode, request.POST, app_label, model_name, skip_first)

    elif request.POST and action == 'export':
        return csv_export(request, app_label, model_name, encoding, delimiter)


    return render_to_response('admin/import_form.html',
                              { 'title' : _('CSV Import / Export'),
                                'fields' : fields,
                                'output' : output,
                                'input' : input,
                                'form' : form,
                                'cl' : ChangeList(request, admin_obj.model,
                                                  admin_obj.list_display,
                                                  admin_obj.list_display_links,
                                                  admin_obj.list_filter,
                                                  admin_obj.date_hierarchy,
                                                  admin_obj.search_fields,
                                                  admin_obj.list_select_related,
                                                  admin_obj.list_per_page,
                                                  admin_obj),
                                'model_name' : model.__name__,
                                'app_label' : app_label
                                },
                              context_instance=RequestContext(request))




def csv_export(request, app_label, model_name, encoding, delimiter):
    model = models.get_model(app_label, model_name)
    if model is None:
        raise Http404("App %r, model %r, not found" % (app_label, model_name))
    opts = model._meta
    try:
        admin_obj = admin.site._registry[model]
    except KeyError:
        raise http.Http404("This model exists but has not been registered with the admin site.")

    if not request.user.has_perm(app_label + '.' + model._meta.get_change_permission()):
        raise PermissionDenied

    max_show_all_allowed = main.MAX_SHOW_ALL_ALLOWED
    main.MAX_SHOW_ALL_ALLOWED = 1000000
    request.META['QUERY_STRING'] = '&'.join(request.POST.getlist('filter'))
    cl = ChangeList(request, admin_obj.model, admin_obj.list_display,
                    admin_obj.list_display_links, admin_obj.list_filter,
                    admin_obj.date_hierarchy, admin_obj.search_fields,
                    admin_obj.list_select_related, admin_obj.list_per_page,
                    admin_obj)
    field_sets = admin_obj.opts.fields
    keys = []
    for field in field_sets:
        if request.POST.has_key(field.name):
            keys.append(field.name)

    response = HttpResponse()
    response['Content-Type'] = "text/csv; charset=%s" % encoding
    response['Content-Disposition'] = 'attachment; filename="contacts.csv"'
    out = csv.writer(response, delimiter = str(delimiter))
    out.writerow(keys)
    for ob in cl.result_list:
        row = []
        for key in keys:
            try:
                value = str(getattr(ob, key))
            except:
                value = getattr(ob, key).encode('utf8')
            value = value != 'None' and unicode(value, 'utf8', errors='replace').encode(encoding, 'replace') or ''
            row.append(value)
        out.writerow(row)
    main.MAX_SHOW_ALL_ALLOWED = max_show_all_allowed
    return response





def csv_import(csv_data, encoding, delimiter, import_mode, form, app_label, model_name, skip_first):
    model = models.get_model(app_label, model_name)
    if model is None:
        raise Http404("App %r, model %r, not found" % (app_label, model_name))

    field_sets = model._meta.admin.get_field_sets(model._meta)

    csv_data = cStringIO.StringIO(csv_data)
    csv_reader = csv.reader(utf8_encoder(csv_data, encoding), delimiter = str(delimiter))
    message = []
    test_message = []
    if not form:
        csv_fields = csv_reader.next()
    else:
        csv_fields = form.keys()

    fields = []
    mandatory_fields = []
    unique_fields = []
    for field_set in field_sets:
        for field_line in field_set.field_lines:
            for field in field_line.fields:
                if field.name in csv_fields:
                    fields.append(field)
                    if not field.null:
                        mandatory_fields.append(field)
                    if field.unique:
                        unique_fields.append(field)

    if import_mode == 'test':
        test_message = [ [field.name for field in fields] ]

    dict_entities = {}
    for field in fields:
        if field.rel and not field.rel.raw_id_admin:
            entity = field.rel.to
            primary_key_field = field.rel.field_name
            dict_entities[entity] = {}
            for e in entity.objects.all():
                dict_entities[entity][str(e)] = getattr(e, primary_key_field)

    nbcols = len(fields)
    n = 0
    for row in csv_reader:
        n += 1
        if skip_first and n == 1:
            continue
        dict_row = {}
        dict_unique_fields = {}
        i = 0
        if len(row) != nbcols:
            message.append("ERROR : %d columns on line %d instead of %d : %s" % (len(row), n, nbcols, `row`))
            break

        for cell in row:
            field = fields[i]
            if field.rel:
                if not field.rel.raw_id_admin:
                    cell = dict_entities[field.rel.to].get(cell, None)
                dict_row[field.name + '_id'] = cell
            else:
                dict_row[field.name] = cell
            i += 1

        for field in unique_fields:
            dict_unique_fields[field.name] = dict_row[field.name]
        if '' in dict_unique_fields.values():
            message.append("Unique fields not filled for this row : (pass)\n%s" % `row`)
            continue

        objects = model.objects.filter(**dict_unique_fields)
        if len(objects) > 1:
            message.append("Too many (%s) objects for %s.objects.filter(%s) : %s" % \
                           (len(objects), model_name, `dict_unique_fields`))
            break
        if import_mode == 'test':
            test_message.append(row)
            j = 0
            test_row = []
            for field in fields:
                cell = "%s" % dict_row.get(field.name, dict_row.get(field.name+'_id'))
                if cell != row[j]:
                    cell = "%s (%s)" % (cell, row[j])
                test_row.append(cell)
                j += 1
            test_message.append(test_row)

        if import_mode == 'delete':
            if objects:
                object = objects[0]
                object.delete()
            else:
                message.append("%s not found" % `dict_unique_fields`)
            continue
        if objects:
            object = objects[0]
            if import_mode == 'add':
                message.append("%s already exists" % `dict_unique_fields`)
                continue
            else:
                for key, value in dict_row.items():
                    if value:
                        setattr(object, key, value)
        else:
            object = model(**dict_row)
        if import_mode in ('add', 'change'):
            safe_save(object)
            object.save()
    else:
        transaction.commit()
        message.append('%d lines succesdfully procedeed' % n)
        return (message, test_message)
    transaction.rollback()
    message.append('%d lines procedeed with error (no change).' % n)
    return (message, test_message)


csv_import = transaction.commit_manually(csv_import)

