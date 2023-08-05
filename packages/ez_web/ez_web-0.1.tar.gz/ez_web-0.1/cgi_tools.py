
def get_form():
    import cgi
    cgi_form = cgi.FieldStorage()
    return get_form_from_FieldStorage(cgi_form)


def get_form_from_FieldStorage(cgi_form):
    form = {}
    for key in cgi_form.keys():
	if not hasattr(cgi_form[key], 'file'):
	    form[key] = cgi_form[key].value
	else:
	    form[key] = cgi_form[key]
	    pass
	pass
    return form


def get_env():
    import os
    os_env = os.environ
    env = dict(os_env)
    return env

