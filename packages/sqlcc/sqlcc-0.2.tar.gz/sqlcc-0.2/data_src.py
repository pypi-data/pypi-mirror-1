import sql


def ds_define():
    import sys
    from pythk.types import is_subclass, is_lambda
    frame = sys._getframe(1)
    tables = [(key, value) for key, value in frame.f_locals.items() if is_subclass(value, sql.table)]
    vview_gen = [(key, value) for key, value in frame.f_locals.items() if is_lambda(value)]
    ds_queries = [(key, value) for key, value in frame.f_locals.items() if isinstance(value, ds_query)]
    return tables, vview_gen, ds_queries


class ds_query(object):
    pass


class vquery(ds_query):
    def __init__(self, vview_gen):
	self.vview_gen = vview_gen
	pass
    
    def __get__(self, instance, owner):
	def cmd(*args):
	    if hasattr(self, 'qstr'):
		qstr = self.qstr
	    else:
		qstr = str(self.vview_gen())
		self.qstr = qstr
		pass
	    cu = instance.get_cursor()
	    cu.execute(qstr, args)
	    return cu.fetchone()[0]
	return cmd
    pass


class squery(ds_query):
    def __init__(self, field_names, vview_gen):
	self.field_names = field_names
	self.vview_gen = vview_gen
	pass
    
    def __get__(self, instance, owner):
	def cmd(*args):
	    from pythk.conveniences import combine_sequences
	    if hasattr(self, 'qstr'):
		qstr = self.qstr
	    else:
		self.qstr = qstr = str(self.vview_gen())
		pass
	    cu = instance.get_cursor()
	    cu.execute(qstr, args)
	    row = cu.fetchone()
	    return dict(combine_sequences(self.field_names, row))
	return cmd
    pass


class mquery(ds_query):
    def __init__(self, field_names, vview_gen):
	self.field_names = field_names
	self.vview_gen = vview_gen
	pass
    
    def __get__(self, instance, owner):
	def cmd(*args):
	    from pythk.conveniences import combine_sequences
	    if hasattr(self, 'qstr'):
		qstr = self.qstr
	    else:
		self.qstr = qstr = str(self.vview_gen())
		pass
	    cu = instance.get_cursor()
	    cu.execute(qstr, args)
	    rows = cu.fetchall()
	    return [dict(combine_sequences(self.field_names, row)) for row in rows]
	return cmd
    pass


class data_src_meta(type):
    def __new__(M, name, bases, dict):
	try:
	    ds_definition = dict['ds_definition']
	except KeyError:
	    pass
	else:
	    tables, vview_gens, ds_queries = ds_definition()
	    all_tbs = []
	    
	    del dict['ds_definition']
	    
	    for name, tb_class in tables:
		dict[name] = tb_class
		all_tbs.append(tb_class)
		pass
	    
	    for name, vview_gen in vview_gens:
		data_src = data_src_meta.make_query_cmd_from_view_gen(name, vview_gen)
		dict[name] = data_src
		pass
	    
	    for name, a_ds_query in ds_queries:
		dict[name] = a_ds_query
		pass
	    
	    dict['_all_tbs'] = all_tbs
	    pass
	
	return type.__new__(M, name, bases, dict)
    
    class make_query_cmd_from_view_gen(object):
	def __init__(self, var_name, view_generator):
	    self.var_name = var_name
	    self.view_generator = view_generator
	    pass
	
	def __get__(self, instance, owner):
	    def cmd(*args):
		if hasattr(self, 'qstr'):
		    qstr = self.qstr
		else:
		    qstr = str(self.view_generator())
		    self.qstr = qstr
		    pass
		cu = instance.get_cursor()
		cu.execute(qstr, args)
		return cu
	    
	    return cmd
	
	def __set__(self, instance, value):
	    raise AttributeError()
	
	def __delete__(self, instance):
	    raise AttributeError()
	pass
    pass


class data_src(object):
    __metaclass__ = data_src_meta
    
    def __init__(self, db_conn):
	super(data_src, self).__init__()
	self.cx = db_conn
	pass
    
    def init_db(self):
	cu = self.get_cursor()
	for tb in self._all_tbs:
	    qstr = tb.schema
	    cu.execute(qstr)
	    pass
	pass
    
    def insert(self, table, **kws):
	cu = self.get_cursor()
	cmd = apply(table.factory, (), kws).gen_insert_cmd()
	cu.execute(cmd)
	return cu
    
    def update(self, table, **kws):
	cu = self.get_cursor()
	if kws.has_key('where'):
	    cond = kws['where']
	    kws = dict(kws)
	    del kws['where']
	else:
	    cond = None
	    pass
	values_o = apply(table.factory, (), kws)
	
	cmd = values_o.gen_update_cmd(cond)
	cu.execute(cmd)
	return cu
    
    def delete(self, table, where=None):
	cu = self.get_cursor()
	cmd = table.gen_delete_cmd(where)
	cu.execute(cmd)
	return cu
    
    def get_cursor(self):
	return self.cx.cursor()
    
    def commit(self):
	self.cx.commit()
	pass
    
    def rollback(self):
	self.cx.rollback()
	pass
    
    @staticmethod
    def clone_tb(tb):
	assert isinstance(tb, sql.table)
	return tb.__class__()
    pass


