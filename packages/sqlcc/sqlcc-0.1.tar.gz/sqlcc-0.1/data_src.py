import sql


def ds_define():
    import sys
    from pythk.types import is_subclass, is_lambda
    frame = sys._getframe(1)
    tables = [(key, value) for key, value in frame.f_locals.items() if is_subclass(value, sql.table)]
    vview_gen = [(key, value) for key, value in frame.f_locals.items() if is_lambda(value)]
    return tables, vview_gen


class data_src_meta(type):
    def __new__(M, name, bases, dict):
	try:
	    ds_definition = dict['ds_definition']
	except KeyError:
	    pass
	else:
	    tables, vview_gens = ds_definition()
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
    
    def get_cursor(self):
	return self.cx.cursor()
    
    def commit(self):
	self.cx.commit()
	pass
    
    @staticmethod
    def clone_tb(tb):
	assert isinstance(tb, sql.table)
	return tb.__class__()
    pass


if __name__ == '__main__':
    from pysqlite2 import dbapi2 as sqlite
    
    class my_data_src(data_src):
	def ds_definition():
	    class t1(sql.table):
		item = sql.str_f()
		count = sql.int_f()
		pass
	    
	    class t2(sql.table):
		item = sql.str_f()
		money = sql.float_f()
		pass
	    
	    get_count_and_money_of_item = \
	    lambda: (t1 * t2) \
	    .fields(t1.item, t1.count * t2.money - 30) \
	    .where((t1.item == t2.item) & (t1.item != sql._q))
	    
	    return ds_define()
	pass
    
    cx = sqlite.connect('test.db')
    db = my_data_src(cx)
    db.init_db()
    db.insert(db.t1, item='foo', count=100)
    db.insert(db.t2, item='foo', money=3.2)
    db.insert(db.t1, item='boo', count=50)
    db.insert(db.t2, item='boo', money=3.0)
    db.update(db.t1, count=140, where=~(db.t1.item == 'foo'))
    cu = db.get_count_and_money_of_item('foo')
    rows = cu.fetchall()
    print rows
    cu = db.get_count_and_money_of_item('cool')
    rows = cu.fetchall()
    print rows
    db.commit()
    pass

