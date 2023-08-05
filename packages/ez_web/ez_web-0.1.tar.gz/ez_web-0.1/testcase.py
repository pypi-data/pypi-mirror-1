import unittest
import rpc


def test(stub_o, verify, testcase):
    from pythk.iters import iter_factory, all_combines, all_enum
    astr = 'ab'
    bstr = 'cd'
    argss = [range(i) for i in range(len(astr) + 3)]
    good_factory = iter_factory(lambda: all_combines(astr))
    bad_factory = iter_factory(lambda: all_combines(bstr))
    for args, good, bad in all_enum(argss, good_factory, bad_factory):
	want_success = verify(args, good, bad)
	kws = dict.fromkeys(good + bad)
	try:
	    stub_o(*args, **kws)
	    success = True
	except TypeError, e:
	    success = False
	    pass
	testcase.assertEqual(want_success, success)
	pass
    pass
    
    
class verify(object):
    def __init__(self, varargs, varkws, defaults):
	super(verify, self).__init__()
	self.varargs = varargs
	self.varkws = varkws
	self.defaults = defaults
	pass
	
    def __call__(self, args, good, bad):
	from itertools import izip
	astr='ab'
	bstr = 'cd'
	
	if not self.varargs and len(args) > len(astr):
	    return False
	    
	args_cnt = dict.fromkeys(astr + bstr, 0)
	args_cnt.setdefault(0)
	    
	for k, v in izip(astr, args):
	    args_cnt[k] += 1
	    pass
	for k in good:
	    args_cnt[k] += 1
	    pass
	for k in bad:
	    args_cnt[k] += 1
	    pass
	defaults = self.defaults
	for k in (defaults or []) and astr[-defaults:]:
	    args_cnt[k] = args_cnt[k] or 1
	    pass
	    
	for k in astr:
	    if args_cnt[k] != 1:
		return False
	    pass
	if not self.varkws:
	    for k in bad:
		if args_cnt[k] == 1:
		    return False
		pass
	    pass
	return True
    pass


class rpc_testcase(unittest.TestCase):
    def testRpcStub1(self):
	ns = rpc.simple_ns()
	facto = rpc.stub_factory(ns)
	def foo(a, b, *args, **kws):
	    pass
	stub_o = facto.get_rpc_stub(foo, ns)
	test(stub_o, verify(True, True, 0), self)
	pass
    
    def testRpcStub2(self):
	ns = rpc.simple_ns()
	facto = rpc.stub_factory(ns)
	def foo(a, b=1, *args, **kws):
	    pass
	stub_o = facto.get_rpc_stub(foo, ns)
	test(stub_o, verify(True, True, 1), self)
	pass
    
    def testRpcStub3(self):
	ns = rpc.simple_ns()
	facto = rpc.stub_factory(ns)
	def foo(a, b, **kws):
	    pass
	stub_o = facto.get_rpc_stub(foo, ns)
	test(stub_o, verify(False, True, 0), self)
	pass
    
    def testRpcStub4(self):
	ns = rpc.simple_ns()
	facto = rpc.stub_factory(ns)
	def foo(a, b=1, **kws):
	    pass
	stub_o = facto.get_rpc_stub(foo, ns)
	test(stub_o, verify(False, True, 1), self)
	pass
    
    def testRpcStub5(self):
	ns = rpc.simple_ns()
	facto = rpc.stub_factory(ns)
	def foo(a, b, *args):
	    pass
	stub_o = facto.get_rpc_stub(foo, ns)
	test(stub_o, verify(True, False, 0), self)
	pass
    
    def testRpcStub6(self):
	ns = rpc.simple_ns()
	facto = rpc.stub_factory(ns)
	def foo(a, b=1, *args):
	    pass
	stub_o = facto.get_rpc_stub(foo, ns)
	test(stub_o, verify(True, False, 1), self)
	pass
    
    def testRpcStub7(self):
	ns = rpc.simple_ns()
	facto = rpc.stub_factory(ns)
	def foo(a, b):
	    pass
	stub_o = facto.get_rpc_stub(foo, ns)
	test(stub_o, verify(False, False, 0), self)
	pass
    
    def testRpcStub8(self):
	ns = rpc.simple_ns()
	facto = rpc.stub_factory(ns)
	def foo(a, b=1):
	    pass
	stub_o = facto.get_rpc_stub(foo, ns)
	test(stub_o, verify(False, False, 1), self)
	pass
    
    def testRpcStub9(self):
	ns = rpc.simple_ns()
	facto = rpc.stub_factory(ns)
	def foo(a=1, b=1):
	    pass
	stub_o = facto.get_rpc_stub(foo, ns)
	test(stub_o, verify(False, False, 2), self)
	pass
    
    def testPackUnpack(self):
	ns = rpc.simple_ns()
	facto = rpc.stub_factory(ns)
	def foo(a, b, *args, **kws):
	    pass
	
	stub_o = facto.get_rpc_stub(foo, ns)
	pkt = stub_o._pack()
	stub_o_r = rpc.rpc_stub._unpack(pkt)
	self.assertEqual(stub_o.__dict__, stub_o_r.__dict__)
	pass
    
    def test_rpc_dispatcher(self):
	import random
	
	ns = rpc.simple_ns()
	facto = rpc.stub_factory(ns)
	class foo(object):
	    def aoo(self, a, b=3):
		pass
	    def coo(self, a, b, *args):
		return a * b * (((not args) and 1) or args[0])
	    def doo(self, a, b, **kws):
		pass
	    pass
	
	foo_o = foo()
	stub_o = facto.get_rpc_obj_stub(foo_o, ns)
	pkt = stub_o._pack()
	stub_o_r = rpc.rpc_obj_stub._unpack(pkt)
	self.assertEqual(stub_o.aoo._pack(), stub_o_r.aoo._pack())
	self.assertEqual(stub_o.coo._pack(), stub_o_r.coo._pack())
	self.assertEqual(stub_o.doo._pack(), stub_o_r.doo._pack())
	
	dis = rpc.rpc_dispatcher(ns)
	for i in range(1000):
	    n1 = random.random() * 1000
	    n2 = random.random() * 1000
	    pkt = stub_o_r.coo(n1, n2)
	    self.assertEqual(dis.dispatch(pkt), n1 * n2)
	    pass
	for i in range(1000):
	    n1 = random.random() * 1000
	    n2 = random.random() * 1000
	    n3 = random.random() * 1000
	    pkt = stub_o_r.coo(n1, n2, n3)
	    self.assertEqual(dis.dispatch(pkt), n1 * n2 * n3)
	    pass
	pass
    
    def test_make_stubs_in_struct(self):
	ns = rpc.simple_ns()
	facto = rpc.stub_factory(ns)
	class foo(object):
	    def kk(self, abc):
		pass
	    pass
	def bar(a,b):
	    pass
	foo_o = foo()
	boo_o = foo()
	
	old_data = (bar, {'bar': bar, 'foo': foo_o}, 'test', (boo_o, 1))
	data = facto.make_stubs_in_struct(old_data)
	
	self.assert_(data is not old_data)
	self.assert_(isinstance(data, tuple))
	
	self.assert_(isinstance(data[0], rpc.rpc_stub))
	self.assertEqual(data[0], ns.find(obj=bar)[rpc.rpc_stub])
	
	self.assert_(data[1] is old_data[1])
	self.assertEqual(data[0], data[1]['bar'])
	self.assert_(isinstance(data[1]['foo'], rpc.rpc_obj_stub))
	self.assertEqual(data[1]['foo'], ns.find(obj=foo_o)[rpc.rpc_obj_stub])
	
	self.assertEqual(data[2], 'test')
	
	self.assert_(data[3] is not old_data[3])
	self.assert_(isinstance(data[3], tuple))
	self.assert_(isinstance(data[3][0], rpc.rpc_obj_stub))
	self.assertEqual(data[3][1], 1)
	pass
    pass


def suite():
    test = [
        'testRpcStub1', 'testRpcStub2', 'testRpcStub3', 'testRpcStub4',
        'testRpcStub5', 'testRpcStub6', 'testRpcStub7', 'testRpcStub8',
        'testRpcStub9', 'testPackUnpack', 'test_rpc_dispatcher',
	'test_make_stubs_in_struct'
    ]
    cases = [rpc_testcase(t) for t in test]
    suite = unittest.TestSuite(cases)
    return suite

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
    pass
