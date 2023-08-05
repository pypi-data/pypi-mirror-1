
class web_engine(object):
    def __init__(self, processors, req_factory=None, err_hdr=None, uerr_hdr=None):
        super(web_engine, self).__init__()
        self.processors = processors
	if req_factory:
	    self.__req_factory = req_factory
	else:
	    self.__req_factory = request
	    pass
	self.err_hdr = err_hdr
	self.uerr_hdr = uerr_hdr
        pass
    
    def process(self, form, env, input_fo, output_fo, error_fo):
        req = self.__req_factory(form, env, input_fo, output_fo, error_fo)
	try:
	    processors = self.processors
	    for p in processors:
		req = p.ingress(req)
		pass
	    for p in reversed(processors):
		req = p.outgress(req)
		pass
	    pass
	except proc_error, e:
	    self.error(e, req)
	except:
	    self.unknow_error(req)
	    pass
	pass
    
    def error(self, e, req):
	if self.err_hdr:
	    self.err_hdr(e, req)
	    return
	import sys, traceback
	_type, value, tb = sys.exc_info()
	req.output_fo.write('Status: ' + str(e.code) + ' ' + e.msg + '\n')
	req.output_fo.write('Content-Type: text/plain\n\n')
	req.output_fo.write(str(e.code) + ' ' + e.msg +'\n\n')
	traceback.print_tb(tb, file=req.output_fo)
	pass
    
    def unknow_error(self, req):
	if self.uerr_hdr:
	    self.uerr_hdr(req)
	    return
	import sys, traceback
	_type, value, tb = sys.exc_info()
	req.output_fo.write('Status: 500 Internal Server Error\n')
	req.output_fo.write('Content-Type: text/plain\n\n')
	req.output_fo.write(str(req.__dict__))
	req.output_fo.write('\n\n')
	req.output_fo.write(_type.__name__ + ': ' + str(value) + '\n')
	traceback.print_tb(tb, file=req.output_fo)
	pass
    pass


class request(object):
    def __init__(self, form, env, input_fo, output_fo, error_fo):
        super(request, self).__init__()
        self.form = form
        self.env = env
        self.input_fo = input_fo
	self.output_fo = output_fo
	self.error_fo = error_fo
        pass
    
    def created(self, location):
	self.status = 201
	self.location = location
	pass
    
    def no_content(self):
	self.status = 204
	pass
    
    def redirect(self, location):
	self.status = 302
	self.location = location
	pass
    
    def precondition_failed(self):
	self.status = 412
	pass
    
    def method_not_allowed(self):
	self.status = 405
	pass
    
    def not_found(self):
	self.status = 404
	pass
    
    def forbidden(self):
	self.status = 403
	pass
    
    def unauthorized(self):
	self.status = 401
	pass
    
    def bad_request(self):
	self.status = 400
	pass
    pass


class proc_error(Exception):
    def __init__(self, code=404, msg='not found'):
	self.code = code
	self.msg = msg
	pass
    pass


class processor(object):
    def __init__(self):
        super(processor, self).__init__()
        pass
    
    def ingress(self, req):
        return req
    
    def outgress(self, req):
        return req
    pass


class status_proc(processor):
    msg = { 404: '404 not found' }
    def outgress(self, req):
	if hasattr(req, 'status'):
	    req.output_fo.write('Status: ' + msg[req.status] + '\n')
	    pass
	return req
    pass


class header_proc(processor):
    def ingress(self, req):
	req.env['HEADERS_OUT'] = {}
	return req
	pass
    
    def outgress(self, req):
	if req.env['HEADERS_OUT']:
	    headers = req.env['HEADERS_OUT']
	    for k, v in headers.iteritems():
		req.output_fo.write(k + ': ' + v + '\n')
		pass
	    pass
	return req
    pass


class mime_proc(processor):
    def outgress(self, req):
	if hasattr(req, 'mime_type'):
	    mime = req.mime_type
	else:
	    mime = 'text/html'
	    pass
	if mime:
	    req.output_fo.write('Content-Type: ' + mime + '\n\n')
	    pass
	return req;
    pass


class path_to_mod_proc(processor):
    def outgress(self, req):
	from tools import partial_import
	import string
	env = req.env
	try:
	    path = env['PATH_INFO']
	except KeyError:
	    path = '/'
	    pass
	
	pparts = path.split('/')
	pparts = ['ez_controls'] + [part for part in pparts if part]
	
	mod, pparts, i = partial_import(pparts)
	
	if not hasattr(mod, 'process'):
	    raise proc_error(404, 'can not load module "' + string.join(pparts, '.') + '", stop at "' + string.join(pparts[:i], '.') + '"')
	
	saved_path = env['PATH_INFO']
	env['PATH_INFO'] = '/' + string.join(pparts[i:], '/')
	try:
	    mod.process(req)
	finally:
	    env['PATH_INFO'] = saved_path
	    pass
	return req
    pass

