
class scope(object):
    def __init__(self, temp, func, name):
	super(scope, self).__init__()
	self.temp = temp
	self.name = name
	self.func = func
	pass
    
    def __enter__(self):
	temp = self.temp
	name = self.name
	top = temp.nss[-1]
	if top.has_key(name):
	    if isinstance(top[name], dict):
		top[name] = [top[name]]
		pass
	    if isinstance(top[name], list):
		ntop = {}
		top[name].append(ntop)
		pass
	    pass
	else:
	    ntop = top[name] = {}
	    pass
	temp.nss.append(ntop)
	return temp
    
    def __exit__(self, exc_type, exc_value, traceback):
	self.temp.nss.pop()
	pass
    
    def __call__(self, *args, **kws):
	return self.func(self.temp, *args, **kws)
    
    def set_var(self, var):
	if not isinstance(var, (dict, list, tuple)):
	    raise TypeError, 'var should be type of dict, list or tuple'
	ntop = self.temp.nss[-1]
	ntop[self.name] = var
	pass
    pass

class scope_deco(object):
    def __init__(self, name, func):
	super(scope_deco, self).__init__()
	self.func = func
	self.name = name
	pass
    
    def __get__(self, temp, owner):
	return scope(temp, self.func, self.name)
    
    def __set__(self, temp, value):
	top = temp.nss[-1]
	top[self.name] = value
	pass
    pass

class new_web_meta(type):
    def __init__(clz, name, bases, dict):
	super(new_web_meta, clz).__init__(name, bases, dict)
	for name in dict.keys():
	    if not name.startswith('_'):
		func = dict[name]
		setattr(clz, name, scope_deco(name, func))
	    pass
	pass
    pass

class nez_web(object):
    __metaclass__ = new_web_meta
    
    def __init__(self):
	super(nez_web, self).__init__()
	pass
    
    def __enter__(self):
	self.rootns = {}
	self.nss = [self.rootns]
	pass
    
    def __exit__(self, exc_type, exc_value, traceback):
	self._root({}, self.rootns)
	pass
    
    def _feed_subtree(self, temp, pdata, cdata):
	if isinstance(cdata, dict):
	    data = dict(pdata)
	    data.update(cdata)
	    temp(data)
	elif isinstance(cdata, list):
	    for d in cdata:
		data = dict(pdata)
		data.update(d)
		temp(data)
		pass
	    pass
	else:
	    self.ofo.write(cdata)
	    pass
	pass
    pass

