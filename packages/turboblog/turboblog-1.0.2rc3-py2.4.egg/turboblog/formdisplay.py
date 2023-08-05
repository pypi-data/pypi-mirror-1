'''
a small helper for widgets
'''

def form_display(form, params):
    value=dict()
    options=dict()

    if 'values' in params.keys():
        for key in params['values']:
            value[key] = params['values'][key] 

    if 'options' in params.keys():
        for key in params['options']:
            options[key] = params['options'][key]

    return form.display(value, options=options)

# vim: expandtab tabstop=4 shiftwidth=4:
