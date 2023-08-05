'''
A simple implementation of RPC.  It leverages power of Python module 'pickle'
and Dynamic Typing.
'''
from pythk.decorators import catch_on

# ============================================================
# Name service
#
class rpc_ns(object):
    '''
    Name service inteface
    '''
    def regeister(self, obj):
	'''
	Creates a entity and associates with a object.
	'''
	pass
    def unregister(self, en_o):
	pass
    def find(self, obj=None, oid=None):
	'''
	Find a entity with a object or a OID.
	'''
	pass
    pass


class rpc_ns_entity(object):
    '''
    Entity represents a entry create by a name service.
    
    Entity is a entry for a name, it saves attributes for a name.
    A entity is saw as a dictionary that can keep any type of data.
    Each entity is associated with a OID (rpc_ns_entity.oid).  It
    can be used as a key to retrive the entity.
    '''
    def __init__(self, oid, ns=None):
	super(rpc_ns_entity, self).__init__()
	self.oid = oid
	self.ns = ns
	pass
    
    def get_obj(self):
	'''
	Get object of the entity.
	'''
	pass
    
    def __getitem__(self, key):
	pass
    
    def __setitem__(self, key):
	pass
    pass


class simple_ns(rpc_ns):
    '''
    Simple implementation of rpc_ns.
    '''
    class entity(rpc_ns_entity):
	'''
	Simple implementation of rpc_ns_entity.
	'''
	def __init__(self, oid, ns=None):
	    super(simple_ns.entity, self).__init__(oid, ns)
	    self.__attrs = {}
	    pass
	
	def get_obj(self):
	    return self.ns.get_obj(self)
	
	def __getitem__(self, key):
	    return self.__attrs[key]
	
	def __setitem__(self, key, value):
	    self.__attrs[key] = value
	    pass
	pass
    
    def __init__(self):
	super(simple_ns, self).__init__()
	self.__obj_entity = {}
	self.__oid_entity = {}
	pass
    
    @catch_on(KeyError, lambda: None)
    def register(self, obj):
	if self.__obj_entity.has_key(obj):
	    return self.__obj_entity[obj]
	oid = id(obj)
	en_o = simple_ns.entity(oid, self)
	en_o.__obj = obj
	self.__obj_entity[obj] = en_o
	self.__oid_entity[oid] = en_o
	return en_o
    
    def unregister(self, en_o):
	del self.__obj_entity[en_o.get_obj()]
	del self.__oid_entity[en_o.oid]
	pass
    
    @catch_on(KeyError, lambda: None)
    def find(self, obj=None, oid=None):
	if obj:
	    return self.__obj_entity[obj]
	return self.__oid_entity[oid]
    
    @staticmethod
    @catch_on(KeyError, lambda: None)
    def get_obj(en_o):
	return en_o.__obj
    pass


# ============================================================
# RPC stubs
#
class rpc_stub(object):
    '''rpc_stub implements stub for a remote function of method call.'''
    def __init__(self, code, args, varargs, varkws, defaults, im_self=None, end_point=None, piggy=None):
	super(rpc_stub, self).__init__()
	self.code = code
	self.args_names = args
	self.varargs_name = varargs
	self.kws_name = varkws
	self.defaults = defaults
	self.im_self = im_self
	self.end_point = end_point
	self.piggy = piggy
	self.im_name = None
	pass
    
    def __str__(self):
	fmt = '<%s code: %s, args_names: %s, varargs_name: %s, kws_name: %s, defaults: %s, im_self: %s, end_point: %s, piggy: %s, im_name: %s>'
	data = (self.__class__.__name__, self.code, self.args_names, self.varargs_name, self.kws_name, self.defaults, self.im_self, self.end_point, self.piggy, self.im_name)
	data = tuple([str(item) for item in data])
	return fmt % data
    
    def __check_args(self, args, kws):
	from itertools import islice
	
	def error_fmt():
	    if not self.defaults:
		if max_args == 1:
		    fmt = '%s() takes exactly %d argument (%d geven)'
		else:
		    fmt = '%s() takes exactly %d arguments (%d given)'
		    pass
		pass
	    else:
		if max_args == 1:
		    fmt = '%s() takes at most %d argument (%d given)'
		else:
		    fmt = '%s() takes at most %d arguments (%d given)'
		    pass
		pass
	    return fmt
	
	max_args = len(self.args_names)
	n_defaults = (self.defaults or 0) and len(self.defaults)
	
	# calc num of varargs
	n_args = len(args)
	if n_args > max_args:
	    n_varargs = n_args - max_args
	    n_args = max_args
	else:
	    n_varargs = 0
	    pass
	
	if not self.varargs_name and n_varargs:
	    fmt = error_fmt()
	    raise TypeError(fmt % (self.code, max_args, n_args + n_varargs))
	
	if kws:
	    # check multiple values
	    args_names = self.args_names
	    names_it = iter(args_names)
	    for arg_name in islice(names_it, n_args):
		if kws.has_key(arg_name):
		    raise TypeError('%s() got multiple values for keyword argument \'%s\'' % (self.code, arg_name))
		pass
	    
	    # check not specified variables (not in kws)
	    no_default_remains = max_args - n_args - n_defaults
	    if no_default_remains < 0:
		no_default_remains = 0
		pass
	    by_kws = 0
	    for arg_name in islice(names_it, no_default_remains):
		if not kws.has_key(arg_name):
		    fmt = error_fmt()
		    raise TypeError(fmt % (self.code, max_args, n_args + by_kws))
		by_kws += 1
		pass
	    
	    if not self.kws_name:
		# check unknow keywords in kws
		func_args = dict.fromkeys(self.args_names)
		for kw in kws:
		    if not func_args.has_key(kw):
			fmt = '%s() got an unexpected keyword argument \'%s\''
			raise TypeError(fmt % (self.code, kw))
		    pass
		pass
	    pass
	elif (n_args + n_defaults) < max_args:
	    fmt = error_fmt()
	    raise TypeError(fmt % (self.code, max_args, n_args))
	pass
    
    def __call__(self, *args, **kws):
	self.__check_args(args, kws)
	pkt = self._gen_pkt(args, kws)
	return self.send(pkt)
    
    def _gen_pkt(self, args, kws):
	from types import InstanceType, TypeType
	pkt = {'code': self.code, 'args': args, 'kws': kws}
	if self.im_self:
	    pkt['im_self'] = self.im_self
	    pass
	
	return pkt
    
    def send(self, pkt):
	'''
	Send a RPC packet (pkt) to a remote server.
	
	pkt is a dictionary of {'code': ..., 'args': (...), 'kws': {...}}
	'''
	return pkt
    
    @staticmethod
    def _unpack(pkt, stub_clazz=None):
	stub_clazz = stub_clazz or rpc_stub
	
	code = pkt['code']
	args_names = pkt['args_names']
	varargs_name = pkt.setdefault('varargs_name', None)
	kws_name = pkt.setdefault('kws_name', None)
	defaults = pkt.setdefault('defaults', None)
	im_self = pkt.setdefault('im_self', None)
	end_point = pkt.setdefault('end_point', None)
	piggy = pkt.setdefault('piggy')
	im_name = pkt.setdefault('im_name')
	
	stub_o = stub_clazz(code, args_names, varargs_name, kws_name, defaults, im_self, end_point, piggy)
	stub_o.im_name = im_name
	return stub_o
    
    def _pack(self):
	pkt = {'code': self.code, 'args_names': self.args_names}
	if self.varargs_name:
	    pkt['varargs_name'] = self.varargs_name
	    pass
	if self.kws_name:
	    pkt['kws_name'] = self.kws_name
	    pass
	if self.defaults:
	    pkt['defaults'] = self.defaults
	    pass
	if self.im_self:
	    pkt['im_self'] = self.im_self
	    pass
	if self.end_point:
	    pkt['end_point'] = self.end_point
	    pass
	if self.piggy:
	    pkt['piggy'] = self.piggy
	    pass
	if self.im_name:
	    pkt['im_name'] = self.im_name
	return pkt
    pass


class rpc_obj_stub(object):
    '''
    Implements RPC object stub.
    '''
    def __init__(self, obj, method_stubs, end_point=None, piggy=None):
	super(rpc_obj_stub, self).__init__()
	self._obj = obj
	self._end_point = end_point
	self._piggy = piggy
	self._method_stubs = method_stubs
	for method_stub in method_stubs:
	    setattr(self, method_stub.im_name, method_stub)
	    pass
	pass
    
    def __str__(self):
	import string
	fmt = '<%s obj: %s, end_point: %s, piggy: %s, method_stubs: %s>'
	data = (self.__class__.__name__, self._obj, self._end_point, self._piggy, self._method_stubs)
	data = tuple([str(item) for item in data])
	return fmt % data
    
    _stub_clazz = rpc_stub
    
    @staticmethod
    def _unpack(pkt, obj_stub_clazz=None):
	obj_stub_clazz = obj_stub_clazz or rpc_obj_stub
	stub_clazz = obj_stub_clazz._stub_clazz
	method_unpack = stub_clazz._unpack
	
	obj = pkt['obj']
	method_stubs = [method_unpack(m, stub_clazz) for m in pkt['method_stubs']]
	end_point = pkt.setdefault('end_point', None)
	piggy = pkt.setdefault('piggy', None)
	
	return obj_stub_clazz(obj, method_stubs, end_point, piggy)
    
    def _pack(self):
	pkt = {'obj': self._obj, 'method_stubs': [m._pack() for m in self._method_stubs]}
	if self._end_point:
	    pkt['end_point'] = self._end_point
	    pass
	if self._piggy:
	    pkt['piggy'] = self._piggy
	    pass
	return pkt
    pass


# ============================================================
# RPC stub factory & dispatcher
#
class stub_factory(object):
    '''
    Factory provides a set of functions to create stubs.
    
    Stub_factory associates ns and stubs.  It creates stubs and registers
    them with a ns for later using by rpc_dispatcher instances.
    '''
    def __init__(self, ns, stub_clazz=rpc_stub, obj_stub_clazz=rpc_obj_stub, end_point=None):
	super(stub_factory, self).__init__(self)
	self.ns = ns
	self.stub_clazz = stub_clazz
	self.obj_stub_clazz = obj_stub_clazz
	self.end_point = end_point
	pass
    
    def make_stubs_in_struct(self, d):
	'''
	Find user objects of user defined types, functions, and methods
	in a container, if 'd' is a contiainer, and translates them into
	RPC stubs.
	
	Arguments of a RPC are not always native or builtin types.  For
	user defined types, functions, or methods, we need to translate
	it into a rpc_obj_stub.
	
	Note!!  Translation is doing in the place.  Original objects may
	be modified.
	'''
	from types import FunctionType, MethodType
	
	back_tuples = []
	
	class edge(object):
	    def __init__(self, node, parent_edge=None, parent_key=None):
		self.node = node
		self.parent_edge = parent_edge
		self.parent_key = parent_key
		pass
	    
	    def update_node(self, v):
		pe = self.parent_edge
		pnode = pe.node
		if isinstance(pnode, tuple):
		    back_tuples.append(pe)
		    pnode = list(pnode)
		    pe.update_node(pnode)
		    pass
		self.node = pnode[self.parent_key] = v
		pass
	    pass
	
	root = [d]
	root_edge = edge(root)
	
	taskq = [root_edge]
	for edge_o in taskq:
	    node = edge_o.node
	    if isinstance(node, dict):
		new_tasks = [edge(v, edge_o, k) for k, v in node.iteritems()]
		taskq += new_tasks
	    elif isinstance(node, (list, tuple)):
		new_tasks = [edge(v, edge_o, i) for i, v in enumerate(node)]
		taskq += new_tasks
	    elif isinstance(node, (FunctionType, MethodType)):
		edge_o.update_node(self.get_rpc_stub(node))
	    elif not isinstance(node, (float, int, long, str, unicode)):
		edge_o.update_node(self.get_rpc_obj_stub(node))
		pass
	    pass
	
	for edge_o in back_tuples:
	    edge_o.update_node(tuple(edge_o.node))
	    pass
	return root[0]
    
    def get_rpc_stub(self, callable_o, piggy=None):
	'''
	Translate a function or method into a stub.
	'''
	import inspect
	
	ns = self.ns
	
	code_en_o = ns.find(callable_o)
	if code_en_o:
	    return code_en_o[rpc_stub]
	
	if inspect.ismethod(callable_o):
	    for k, v in inspect.getmembers(callable_o):
		if k == 'im_func':
		    func_obj = v
		elif k == 'im_self':
		    im_self = v
		    pass
		pass
	    im_self = im_self and (ns.find(obj=im_self) or ns.register(im_self)).oid
	else:
	    im_self = None
	    func_obj = callable_o
	    pass
	
	args, varargs, varkws, defaults = inspect.getargspec(func_obj)
	if im_self:
	    args = args[1:]
	    pass
	code_en_o = ns.find(obj=callable_o) or ns.register(callable_o)
	code_oid = code_en_o.oid
	stub_o = self.stub_clazz(code_oid, args, varargs, varkws, defaults, im_self, self.end_point, piggy)
	code_en_o[rpc_stub] = stub_o
	return stub_o
    
    def get_rpc_obj_stub(self, obj, piggy=None):
	'''
	Tranlsate a user defined object into a RPC stub.
	
	Methods in the object are translated into stubs.  Other attributes
	can not access by a remote client directly.  All accessing is performed
	by methods through RPC.
	'''
	from inspect import ismethod
	
	ns = self.ns
	
	obj_en_o = ns.find(obj=obj)
	if obj_en_o:
	    return obj_en_o[rpc_obj_stub]
	obj_en_o = ns.register(obj)
	
	method_stubs = []
	for attr in dir(obj):
	    if attr.startswith('_'):
		continue
	    attr_v = getattr(obj, attr)
	    if ismethod(attr_v):
		method_stub = self.get_rpc_stub(attr_v, piggy)
		method_stub.im_name = attr
		method_stubs.append(method_stub)
		pass
	    pass
	obj_oid = obj_en_o.oid
	stub_o = self.obj_stub_clazz(obj_oid, method_stubs, self.end_point, piggy)
	obj_en_o[rpc_obj_stub] = stub_o
	return stub_o
    pass


class rpc_dispatcher(object):
    '''
    Receives a packet for a RPC and calls repective function or method.
    
    A packet is sent by a function or method stub.  When a client starts
    a RPC by calling stub, then rpc_stub._send() is called with a packet.
    rpc_stub._send() sent the packet to the server site.  The server
    site calls a rpc_dispatcher to dispatch to the respective function or
    method.
    '''
    def __init__(self, ns):
	'''
	Need a ns (name server) to map a code OID to the function or
	method object.
	'''
	super(rpc_dispatcher, self).__init__()
	self.ns = ns
	pass
    
    def dispatch(self, pkt):
	'''
	Receives a packet and calls repective function or method.
	'''
	code = pkt['code']
	code_en_o = self.ns.find(oid=code)
	if not code_en_o:
	    raise ValueError('oid 0x%x is invalid' % (code,))
	callo = code_en_o.get_obj()
	args = pkt['args']
	kws = pkt['kws']
	return callo(*args, **kws)
    pass

