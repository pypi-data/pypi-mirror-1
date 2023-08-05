
class ez_user_auth(object):
    cookie_key = 'EZ_USER_AUTH'
    env_cookie = 'HTTP_COOKIE'
    
    def __init__(self, secret, timeout):
	self.secret = secret
	self.timeout = timeout
	pass
    
    def authorized(self, req, account):
	from Cookie import BaseCookie
	
	cipher = self.__auth_encode(account)
	
	cookie = BaseCookie()
	cookie[self.cookie_key] = cipher
	c = cookie[self.cookie_key]
	c['path'] = '/'
	c['max-age'] = str(self.timeout)
	
	headers = req.env['HEADERS_OUT']
	headers['Set-Cookie'] = cookie.output(header='')
	pass
    
    def authen(self, req):
	from Cookie import BaseCookie
	if not req.env.has_key(self.env_cookie):
	    return None
	cookie = BaseCookie(req.env[self.env_cookie])
	if not cookie.has_key(self.cookie_key):
	    return None
	auth_code = cookie[self.cookie_key].value
	return self.__auth_decode(auth_code)
    
    def touch(self, req):
	if not req.env.has_key(self.env_cookie):
	    return
	
	from Cookie import BaseCookie
	cookie = BaseCookie(req.env[self.env_cookie])
	if not cookie.has_key(self.cookie_key):
	    return
	
	c = cookie[self.cookie_key]
	if self.__auth_decode(c.value):
	    c['max-age'] = str(self.timeout)
	    c['path'] = '/'
	    account = c.value.split(':')[0]
	    cookie[self.cookie_key] = self.__auth_encode(account)
	    
	    headers = req.env['HEADERS_OUT']
	    req.env[self.env_cookie] = headers['Set-Cookie'] = cookie.output(header='')
	    pass
	pass
    
    def __auth_encode(self, account):
	import time, md5
	
	ts = str(int(time.time()))
	key = md5.md5(account + self.secret + ts).hexdigest()
	return account + ':' + key + ':' + ts
    
    def __auth_decode(self, auth_code):
	import md5, time
	pparts = auth_code.split(':')
	account = pparts[0]
	key = pparts[1]
	ts = pparts[2]
	if (time.time() - int(ts)) > self.timeout:
	    return None
	
	check_key = md5.md5(account + self.secret + ts).hexdigest()
	if check_key == key:
	    return account
	return None
    pass


import config
uauth = ez_user_auth(config.auth_secret, config.auth_timeout)

