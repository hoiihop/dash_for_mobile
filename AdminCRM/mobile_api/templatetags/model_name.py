from django import template
 
register = template.Library()
 
 
# @register.simple_tag
# def model_name(value):
#     '''
#     Django template filter which returns the verbose name of a model.
#     '''
#     if hasattr(value, 'model'):
#         value = value.model
 
#     return value._meta.verbose_name.title()
 
 
# @register.simple_tag
# def model_name_plural(value):
#     '''
#     Django template filter which returns the plural verbose name of a model.
#     '''
#     if hasattr(value, 'model'):
#         value = value.model
 
#     return value._meta.verbose_name_plural.title()
 
 
@register.simple_tag
def field_name(instance, field):
    '''
    Django template filter which returns the verbose name of an object's,
    model's or related manager's field.
    ''' 
    return instance._meta.get_field(field).verbose_name

@register.simple_tag
def field_type(instance, field):
    return instance._meta.get_field(field).get_internal_type

@register.simple_tag
def get_model_name(instance):
    return instance._meta.verbose_name.title()

@register.simple_tag
def get_fields_name(instance):
    return [field.verbose_name for field in instance._meta.fields]


@register.simple_tag
def split_text(val):    
    return val.split('-')[0]
