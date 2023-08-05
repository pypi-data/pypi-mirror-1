def ez_import(mod_name):
    mod = __import__(mod_name)
    parts = mod_name.split('.')[1:]
    for part in parts:
	mod = getattr(mod, part)
	pass
    return mod

def partial_import(name_parts):
    assert len(name_parts) > 0
    
    try:
	mod = __import__(name_parts[0])
    except:
	return None, 0
    
    try:
	i = 1
	while i < len(name_parts):
	    if hasattr(mod, 'rewrite_path'):
		name_parts = name_parts[:i] + mod.rewrite_path(name_parts[i:])
		pass
	    name = name_parts[i]
	    __import__(name, mod.__dict__)
	    mod = getattr(mod, name)
	    i = i + 1
	    pass
    except ImportError:
	pass
    return mod, name_parts, i
