from itertools import groupby

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ImproperlyConfigured
from django.db import models

def register_app(app_label):
    model_list=models.get_models(app_label)
    register_model(*model_list)


def _is_synced(*mods):
    from django.db import connection
    all_tables=connection.introspection.table_names()
    return set(connection.introspection.table_name_converter(x._meta.db_table) for x in mods).issubset(all_tables)

def register_model(*model_list):
    if not ContentType._meta.installed:
        raise ImproperlyConfigured("Put 'django.contrib.contenttypes' in your INSTALLED_APPS "
                                   "setting in order to use the helptext application.")

    if not _is_synced(ContentType, FieldHelp):
        # syncdb not run yet -- return silently
        return

    for model in model_list:

        for mod, fields in groupby(model._meta.get_fields_with_model(),
                                   lambda x: x[1]):
            if mod is None:
                mod=model
            if not _is_synced(mod):
                # probably not synced yet
                continue
            fields=[x[0] for x in fields]

            content_type=ContentType.objects.get_for_model(mod)
            for field in (f for f in fields if f.editable and not f.auto_created):
                fh=FieldHelp.objects.filter(content_type=content_type,
                                            field_name=field.name)
                if fh:
                    assert len(fh)==1
                    fh=fh[0]
                else:
                    fh=FieldHelp(content_type=content_type,
                                 field_name=field.name,
                                 help_text=field.help_text,
                                 original_help_text=field.help_text)
                    fh.save()
                field.help_text=FieldHelpProxy(fh)

class FieldHelpProxy(object):
    def __init__(self, fh):
        self.content_type=fh.content_type
        self.field_name=fh.field_name

    def __unicode__(self):
        try:
            fh=FieldHelp.objects.get(content_type=self.content_type,
                                     field_name=self.field_name)
        except FieldHelp.DoesNotExist:
            # shouldn't happen
            return ''
        else:
            return fh.help_text 

class FieldHelp(models.Model):
    content_type=models.ForeignKey(ContentType)
    field_name=models.CharField(max_length=120)
    help_text=models.TextField(blank=True)
    original_help_text=models.TextField(blank=True)

    @property
    def model(self):
        return self.content_type.model_class()
    
    @property
    def field(self):
        return self.model._meta.get_field(self.field_name)


    def app_title(self):
        return self.model._meta.app_label.title()
    app_title.short_description='Application'


    def model_title(self):
        return self.model._meta.verbose_name.title()
    model_title.short_description='Model'


    def field_title(self):
        return self.field.verbose_name.title()
    field_title.short_description='Field'

    class Meta:
        ordering=('content_type', 'field_name')
        unique_together=(('content_type', 'field_name'),)
        verbose_name_plural="Field Help"

    def __repr__(self):
        return '<FieldHelp for %r: %r>' % \
               (self.content_type.name,
                self.help_text)

    def __unicode__(self):
        return u"%s - %s: %s" % (self.model._meta.app_label.title(),
                                 self.model._meta.verbose_name.title(),
                                 self.field.verbose_name.title())
    

    def delete(self):
        self.field.help_text=self.original_help_text
        super(FieldHelp, self).delete()
