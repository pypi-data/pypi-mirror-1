class iter_factory(object):
    def __init__(self, f):
	super(iter_factory, self).__init__()
	self.f = f
	pass
	
    def __iter__(self):
	return self.f()
    pass
	
def all_combines(data):
    from itertools import izip
	
    l = len(data)
    sels = [0] * l
    idx = 0
    while idx < l:
	combine = [d for b, d in izip(sels, data) if b == 1]
	yield combine
	idx = 0
	while idx < l:
	    if sels[idx] == 0:
		sels[idx] = 1
		break
	    sels[idx] = 0
	    idx += 1
	    pass
	pass
    pass
    
def all_enum(*datas):
    l = len(datas)
    its = [iter(data) for data in datas]
    out = [it.next() for it in its]
    i = 0
    while i < l:
	yield out
	i = 0
	while i < l:
	    try:
		out[i] = its[i].next()
		break
	    except StopIteration:
		its[i] = iter(datas[i])
		out[i] = its[i].next()
		i += 1
		pass
	    pass
	pass
    pass
    
