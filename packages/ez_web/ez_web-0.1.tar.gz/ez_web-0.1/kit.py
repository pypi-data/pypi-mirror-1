
def path_consumer(*trans, **kws):
    n_trans = len(trans)
    n_args = kws.setdefault('n_args', 0) or n_trans
    if isinstance(n_args, tuple):
	at_least = n_args[0]
	at_most = (len(n_args) == 1) and 65535 or n_args[1]
    elif isinstance(n_args, int):
	at_least = n_args
	at_most = (n_args == 0) and 65535 or n_args
    else:
	raise ValueError()
    
    def decorator(func):
	def _call(req):
	    pparts = req.env['PATH_INFO'].split('/')
	    pparts = [p for p in pparts if p]
	    if (len(pparts) < at_least) or (len(pparts) > at_most):
		req.bad_request()
		return
	    
	    try:
		for i, p in enumerate(pparts):
		    if i < n_trans:
			pparts[i] = trans[i](p)
			pass
		    pass
		pass
	    except:
		req.bad_request()
		pass
	    func(*([req] + pparts))
	return _call
    
    return decorator


class uauth:
    @staticmethod
    def may_auth(func):
	from ez_user_auth import uauth
	return lambda req, *args: func(*((req, uauth.authen(req)) + args))
    
    @staticmethod
    def need_auth(func):
	from ez_user_auth import uauth
	def call(req, *args):
	    uid = uauth.authen(req)
	    if uid is None:
		req.precondition_failed()
		return req
	    return func(*((req, uid) + args))
	return call
    
    @staticmethod
    def authorized(req, account):
	from ez_user_auth import uauth
	return uauth.authorized(req, account)
    
    @staticmethod
    def touch(req):
	from ez_user_auth import uauth
	uauth.touch(req)
	pass
    pass
