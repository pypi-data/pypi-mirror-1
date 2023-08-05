from web_engine import processor, path_to_mod_proc, web_engine
from ez_xml_p import auto_temp_proc
from mod_python import apache, util
import cgi_tools


status_map = {
201: apache.HTTP_CREATED,
204: apache.HTTP_NO_CONTENT,
302: apache.HTTP_MOVED_TEMPORARILY,
400: apache.HTTP_BAD_REQUEST,
401: apache.HTTP_UNAUTHORIZED,
403: apache.HTTP_FORBIDDEN,
404: apache.HTTP_NOT_FOUND,
405: apache.HTTP_METHOD_NOT_ALLOWED,
412: apache.HTTP_PRECONDITION_FAILED
}


class status_proc(processor):
    def outgress(self, req):
	if hasattr(req, 'status'):
	    req.env['_MOD_PYTHON_REQ'].status = status_map[req.status]
	    if (req.status in (201, 302)) and hasattr(req, 'location'):
		req.env['_MOD_PYTHON_REQ'].headers_out['Location'] = req.location
		pass
	    if req.status == 201:
		req.output_fo.write('OK\n')
		pass
	    if req.status != 204:
		req.output_fo.write(str(req.status) + '\n')
		pass
	    req.no_temp = True
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
	    headers_out = req.env['_MOD_PYTHON_REQ'].headers_out
	    for k, v in headers.iteritems():
		headers_out[k] = v
		pass
	    pass
	return req
    pass


class mime_proc(processor):
    def __init__(self):
	super(mime_proc, self).__init__()
	self.charset = charset
	pass
    
    def outgress(self, req):
	if hasattr(req, 'mime_type'):
	    mime = req.mime_type
	else:
	    if self.charset:
		mime = 'text/html; charset=' + self.charset
	    else:
		mime = 'text/html'
		pass
	    pass
	req.env['_MOD_PYTHON_REQ'].content_type = mime
	return req
    pass


class uauth_touch_proc(processor):
    def outgress(self, req):
	from kit import uauth
	uauth.touch(req)
	return req
    pass


def error_hdr(e, req):
    import traceback, sys, log
    import string
    req.env['_MOD_PYTHON_REQ'].content_type = 'text/plain'
    req.env['_MOD_PYTHON_REQ'].status = status_map[e.code]
    _type, value, tb = sys.exc_info()
    req.output_fo.write(str(e.code) + ' ' + e.msg + '\n\n')
    traceback.print_tb(tb, file=req.output_fo)
    
    log.error(str(e.code) + ' ' + e.msg)
    log.error(string.join(traceback.format_tb(tb)))
    pass


def unknow_error_hdr(req):
    import traceback, sys
    import log, string
    req.env['_MOD_PYTHON_REQ'].content_type = 'text/plain'
    req.env['_MOD_PYTHON_REQ'].status = apache.HTTP_INTERNAL_SERVER_ERROR
    _type, value, tb = sys.exc_info()
    req.output_fo.write(str(req.__dict__))
    req.output_fo.write('\n\n')
    req.output_fo.write(_type.__name__ + ': ' + str(value) + '\n')
    traceback.print_tb(tb, file=req.output_fo)
    
    log.error(str(req.__dict__))
    log.error(_type.__name__ + ': ' + str(value))
    log.error(string.join(traceback.format_tb(tb)))
    pass


#
# A work around to support locale specified encoding
# at str()
#
def initialize():
    # this only works for mod_python
    import locale
    global charset
    locale.setlocale(locale.LC_CTYPE, '')
    charset = locale.getlocale(locale.LC_CTYPE)[1]
    # hack str() to support locale specified encoding
    if charset:
	import codecs
	encoder = codecs.getencoder(charset)
	orig_str = str
	class hack_str(orig_str):
	    def __new__(clazz, x=''):
		if isinstance(x, unicode):
		    x = encoder(x)[0]
		elif not isinstance(x, orig_str):
		    x = orig_str.__new__(clazz, x)
		    pass
		return x
	    pass
	orig_isinstance = isinstance
	def hack_isinstance(x, clss):
	    if type(clss) is not tuple:
		return orig_isinstance(x, ((clss is not hack_str) and clss) or orig_str)
	    clss = tuple([((cls is not hack_str) and cls) or orig_str for cls in clss])
	    return orig_isinstance(x, clss)
	
	__builtins__['str'] = hack_str
	__builtins__['isinstance'] = hack_isinstance
	pass
    pass
initialize()

processors = (\
    auto_temp_proc(), \
    mime_proc(), \
    status_proc(), \
    header_proc(), \
    uauth_touch_proc(), \
    path_to_mod_proc() \
    )
engine = web_engine(processors, err_hdr=error_hdr, uerr_hdr=unknow_error_hdr)

def handler(req):
    cgi_form = util.FieldStorage(req)
    form = cgi_tools.get_form_from_FieldStorage(cgi_form)
    env = dict(req.subprocess_env)
    env['_MOD_PYTHON_REQ'] = req
    if req.headers_in.has_key('Cookie'):
	env['HTTP_COOKIE'] = req.headers_in['Cookie']
	pass
    class fake_file(object):
	pass
    fo = fake_file()
    fo.read = req.read
    fo.write = req.write
    engine.process(form, env, fo, fo, fo)
    return apache.OK

