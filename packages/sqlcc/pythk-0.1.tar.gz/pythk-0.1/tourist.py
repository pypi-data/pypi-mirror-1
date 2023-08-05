#!/usr/local/bin/python

class tnode(object):
    def __init__(self, name, idx, obj, parent):
	super(tnode, self).__init__()
	self.name = name
	self.idx = idx
	self.obj = obj
	self.parent = parent
	try:
	    self.name_path = parent.name_path + (name,)
	except AttributeError:
	    self.anme_path = (name,)
	pass
    pass


class tourist(object):
    primitive_types = (int, long, float, complex, str)
    
    def __init__(self):
	super(tourist,self).__init__()
	pass
    
    def walk(self, name, obj):
	results = []
	if isinstance(obj, (list, tuple)):
	    waiting_objs = [tnode(name, i, o, None) for i, o in enumerate(obj)]
	else:
	    waiting_objs = [tnode(name, 0, obj, None)]
	    pass
	idx = 0
	while len(waiting_objs) > idx:
	    visit = waiting_objs[idx]
	    idx = idx + 1
	    act = self.find_action(visit)
	    if act:
		r = act(visit)
		results.append(r)
	    else:
		self.append_children_on(visit, waiting_objs)
		pass
	    pass
	return results
    
    def find_action(self, visit):
	pass
    
    def append_children_on(self, visit, waiting_objs):
	obj = visit.obj
	if isinstance(obj, self.primitive_types):
	    return
	
	if isinstance(obj, dict):
	    for key in obj:
		new_node = tnode(key, 0, obj[key], visit)
		waiting_objs.append(new_node)
		pass
	    return
	
	for name in obj.__dict__:
	    child = getattr(obj, name)
	    if not isinstance(child, (list, tuple)):
		children = (child,)
	    else:
		children = child
		pass
	    for idx, child in enumerate(children):
		new_node = tnode(name, idx, child, visit)
		waiting_objs.append(new_node)
		pass
	    pass
	pass
    pass


class name_act(object):
    def __init__(self, path, action):
	super(name_act, self).__init__()
	self.path = path
	self.action = action
	pass
    pass


class name_tourist(tourist):
    def __init__(self, actions):
	super(name_tourist, self).__init__()
	self.actions = actions
	pass
    
    def find_action(self, visit):
	for act in self.actions:
	    path = act.path
	    action = act.action
	    traceback = visit
	    rpath = list(path)
	    rpath.reverse()
	    for name in rpath:
		if name != '*' and name != traceback.name:
		    break
		traceback = traceback.parent
		pass
	    else:
		return action
	    pass
	pass
    pass


class isinstance_act(object):
    def __init__(self, clazzz, action):
	super(isinstance_act, self).__init__()
	self.clazzz = clazzz
	self.action = action
	pass
    pass


class isinstance_tourist(tourist):
    def __init__(self, actions):
	super(isinstance_tourist, self).__init__()
	self.actions = actions
	pass
    
    def find_action(self, visit):
	for act in self.actions:
	    if isinstance(visit.obj, act.clazzz):
		return act.action
	    pass
	pass
    pass


if __name__ == '__main__':
    def pname(node):
	return node.name
	pass
    
    class foo(object):
	pass
    
    o = foo()
    o.ll = {}
    o.ll['aa'] = foo()
    o.ll['aa'].bb = 1
    o.bb = foo()
    o.bb.aa = 5
    
    actions = (name_act(('aa', 'bb'), pname),(name_act(('bb', 'aa'), pname)))
    nt = name_tourist(actions)
    print nt.walk('root', o)
    pass
