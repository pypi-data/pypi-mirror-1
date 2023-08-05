'''
a small helper for widgets
'''

def form_display(form, params):
    value=dict()
    options=dict()
    formopts=dict()
    action_set = False
    submit_set = False

    if 'values' in params.keys():
        for key in params['values']:
            value[key] = params['values'][key] 

    if 'options' in params.keys():
        for key in params['options']:
            options[key] = params['options'][key]

    if 'form_opts' in params.keys():
        form_attrs = dict()

        if 'action' in params['form_opts'].keys():
            action_set = True
            action = params['form_opts']['action']
        if 'submit_text' in params['form_opts'].keys():
            submit_set = True
            submit = params['form_opts']['submit_text']

        if 'form_attrs' in params['form_opts'].keys():
            form_attrs = params['form_opts']['form_attrs']

        if action_set and submit_set:
            return form(action=action, submit=submit,
                    value=value, options=options,
                    form_attrs=form_attrs)

        elif action_set:
            return form(action=action,
                    value=value, options=options,
                    form_attrs=form_attrs)

        elif submit_set:
            return form(submit=submit,
                    value=value, options=options,
                    form_attrs=form_attrs)

    return form(value=value, options=options)

# vim: expandtab tabstop=4 shiftwidth=4:
