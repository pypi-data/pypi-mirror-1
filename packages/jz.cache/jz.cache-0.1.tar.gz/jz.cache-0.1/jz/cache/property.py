# zope modules
from zope.component import getUtility, ComponentLookupError
from zope.app.cache.interfaces.ram import IRAMCache

# custom modules
from interfaces import IAnnotationCache, IStaticAnnotationCache
from jz.common import flatten


# Unique empty cache marker:
empty_cache_marker = object()


class CachedFunction(object):
	"""Cached function.

	NOTE: Function call caches are always temporary.
	"""

	def __init__(self, func, key, static=False):
		self.func = func
		self.key = key
		self.static = static

	def _createKey(self, *args):
		"""Create the cache key from the property key and the function arguments."""

		return tuple((self.key,) + tuple(flatten(list(args))))

	def __get__(self, inst, class_=None):
		self.inst = inst
		return self

	def __call__(self, *args):
		try:
			if self.static:
				cache = getUtility(IStaticAnnotationCache)
			else:
				cache = getUtility(IAnnotationCache)
		except ComponentLookupError:
			# Give up on caching.
			return self.func(self.inst, *args)
		key = self._createKey(*args)
		try:
			context = self.inst.context
		except AttributeError:
			context = self.inst
		result = cache.query(context, key, empty_cache_marker)
		if result is empty_cache_marker:
			result = self.func(self.inst, *args)
			cache.set(result, context, key)
		return result


class cachedFunction(object):
	"""Cached function decorator."""

	def __init__(self, key, static=False):
		self.key = key
		self.static = static

	def __call__(self, func):
		return CachedFunction(func, self.key, self.static)


class CachedProperty(object):
	"""Cached property."""

	def __init__(self, func, key, static=False):
		"""
			func: Function wrapped.
			key: Key the cached result is saved under.
			static: Cache persists.
		"""

		self.func = func
		self.key = key
		self.static = static

	def __get__(self, inst, class_=None):
		"""
			Get value
			inst: object instance
			class_: (FIXME?)
		"""

		key = self.key
		# Get cache utility
		try:
			if self.static:
				cache = getUtility(IStaticAnnotationCache)
			else:
				cache = getUtility(IAnnotationCache)
		except ComponentLookupError:
			return self.func(inst)
		# Find object to assign cache for
		try:
			# Were we called from an adapter ?
			ob = inst.context
		except AttributeError:
			ob = inst
		result = cache.query(ob, key, empty_cache_marker)
		if result is empty_cache_marker:
			result = self.func(inst)
			cache.set(result, ob, key)
		return result


class cachedProperty(object):
	"""Cached property decorator."""

	def __init__(self, key, static=False):
		"""
		parameters:
			key: Key the cached result is saved under.
			static: Cache persists.

		"""
		self.key = key
		self.static = static

	def __call__(self, func):
		return CachedProperty(func, self.key, self.static)