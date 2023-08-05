### partial class
###
### This handles partial function application
#################################################################

class partial(object):
	def __init__(self, func, *args, **kwargs):
		if not callable(func):
			raise TypeError("the first argument must be callable")
		
		self.func = func
		self.args = tuple(args)
		self.kwargs = dict(kwargs)
		self._dict = None
		
	def __call__(self, *args, **kwargs):
		applied_args = self.args + args
		
		applied_kwargs = dict(self.kwargs)
		applied_kwargs.update(kwargs)
		
		return self.func(*applied_args, **applied_kwargs)
		
	def _getdict(self):
		if self._dict is None:
			return dict()
		
	def _setdict(self, val):
		assert isinstance(val, dict)
		
		self._dict = val
		
	def _deldict(self):
		raise TypeError("a partial object's dictionary may not be deleted")
		
	__dict__ = property(_getdict, _setdict, _deldict)
	
### foldl
#################################################################
			
def _foldl(func, base, itr):
	try:
		first = itr.next()
	except StopIteration:
		return base

	return _foldl(func, func(base, first), itr)

def foldl(func, base, seq):
	return _foldl(func, base, iter(seq))

### foldr
#################################################################

def _foldr(func, base, itr):
	try:
		first = itr.next()
	except StopIteration:
		return base
		
	return func(first, _foldr(func, base, itr))

def foldr(func, base, seq):
	return _foldr(func, base, iter(seq))
