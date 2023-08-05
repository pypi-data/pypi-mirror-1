class cmp_by_attr:
    def __init__(self, field_name):
	self.field_name = field_name
	pass
    
    def __call__(self, o1, o2):
	return cmp(getattr(o1, self.field_name), getattr(o2, self.field_name))
    pass

def combine_sequences(*args):
    sz = len(args[0])
    for arg in args:
	if len(arg) != sz:
	    raise ValueError('length of sequences are not the same')
	pass
    rseq = []
    for i in range(sz):
	seq = tuple([arg[i] for arg in args])
	rseq.append(seq)
	pass
    return rseq
