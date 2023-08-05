from web_engine import processor, proc_error

class temp_proc(processor):
    def ingress(self, req):
	req.ez_xml_temp = None
	return req
    
    def outgress(self, req):
	if req.ez_xml_temp:
	    req.ez_xml_temp(req.dict_out, req.output_fo)
	else:
	    raise proc_error()
	return req
    pass


class auto_temp_proc(temp_proc):
    def ingress(self, req):
	req.no_temp = False
	return super(auto_temp_proc, self).ingress(req)
    
    def outgress(self, req):
	if req.no_temp:
	    return req
	
	if not req.ez_xml_temp:
	    from tools import partial_import
	    import string
	    
	    try:
		path = req.env['PATH_INFO']
	    except KeyError:
		path = '/'
		pass
	    
	    pparts = path.split('/')
	    pparts = ['ez_templates'] + [part for part in pparts if part]
	    
	    mod, pparts, i = partial_import(pparts)
	    
	    try:
		req.ez_xml_temp = mod.template
	    except AttributeError:
		raise proc_error(404, 'can not load module "' + string.join(pparts, '.') + '", stop at "' + string.join(pparts[:i], '.') + '"')
	    pass
	return super(auto_temp_proc, self).outgress(req)
    pass


def make_stack():
    from web_engine import mime_proc, status_proc, path_to_mod_proc
    stack = []
    stack.append(auto_temp_proc())
    stack.append(mime_proc())
    stack.append(status_proc())
    stack.append(path_to_mod_proc())
    return stack


def run_cgi():
    from web_engine import web_engine
    from cgi_tools import get_form, get_env
    import sys
    
    form = get_form()
    env = get_env()
    processors = make_stack()
    engine = web_engine(processors)
    input_fo, output_fo, error_fo = sys.stdin, sys.stdout, sys.stderr
    engine.process(form, env, input_fo, output_fo, error_fo)
    pass
