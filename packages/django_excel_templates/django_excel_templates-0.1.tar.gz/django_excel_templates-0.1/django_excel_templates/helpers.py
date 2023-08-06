def Break():
      import dbgp.client
      dbgp.client.brk(port=9000)
      
"""  Place to hold helper crud """

import ExcelReports
from django.db.models import related
from django.db.models.fields import AutoField

def get_items(list):
    items = []
    if list.find(',') > 0:
        items = striplist(list.strip(',').split(','))
    else:
        items.append(list.strip())
    return items

def striplist(l):
    list = []
    for x in l:
        list.append(x.strip())
    return list

def isodd(num):
    return num & 1 and True or False

def abstract():
    ''' simple trick to make an abstract base method '''
    import inspect
    caller = inspect.getouterframes(inspect.currentframe())[1][3]
    raise NotImplementedError(caller + ' must be implemented in subclass')

def get_relation_list(model,FK=False):
    """
    Iterates through model to find ManyToMany Fields or ForeignKey Fields.
    Returns dictionary of field names mapped to values.
    """
    results = {}
    for field_list in [model._meta.fields, model._meta.many_to_many]:
        for field in field_list:
            related_model_name = None
            related_model_app_name = None
            if (not field.name[-4:] == '_ptr') and (not field.__class__ == AutoField): 
                if issubclass(field.__class__, related.RelatedField):
                    if not FK:
                        if not field.__class__ == related.ForeignKey:
                            related_model_app_name = field.rel.to.__module__.split('.')[0]
                            if not related_model_app_name == 'django':
                                related_model_name = field.rel.to.__name__
                                full_related_model_name = '.'.join([field.rel.to.__module__, related_model_name])
                                get_values = 'val = model.%s.all()' % field.name
                                exec get_values
                                results[field.name] = val
                            else:
                                continue
                    else:
                        if not field.__class__ == related.ManyToManyField:
                            related_model_app_name = field.rel.to.__module__.split('.')[0]
                            if not related_model_app_name == 'django':
                                related_model_name = field.rel.to.__name__
                                full_related_model_name = '.'.join([field.rel.to.__module__, related_model_name])
                                get_value = 'val = model.%s' % field.name
                                exec get_value
                                results[field.name] = val
                            else:
                                continue

    return results

def convert_to_letter(num):
    alpha = 'abcdefghijklmnopqrstuvwxyz'.upper()
    if num < 26:
        return alpha[num]
    i = 0
    letters = ''
    first_letter = ''
    second_letter =''
    while num > 25:
        first_letter = alpha[i]
        num -= 26
        i += 1
            
    second_letter = alpha[num]
    letters = first_letter + second_letter
    
    return letters
