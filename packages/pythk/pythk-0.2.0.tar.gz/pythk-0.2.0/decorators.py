
def catch_on(excepts, act):
    def get_call(call):
	def calling(*args, **kws):
	    try:
		return call(*args, **kws)
	    except Exception, e:
		pass
	    if not isinstance(e, excepts):
		raise
	    return act()
	return calling
    
    return get_call

class obj_hijack(object):
    def __init__(self, tgt):
	super(obj_hijack, self).__init__()
	self.__tgt = tgt
	pass
    def __getattr__(self, name):
	return getattr(self.__tgt, name)
    pass
