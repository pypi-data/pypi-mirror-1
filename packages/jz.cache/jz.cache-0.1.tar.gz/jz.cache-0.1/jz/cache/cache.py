# zope modules
from zope.interface import implements
from zope.annotation.interfaces import IAnnotations
from zope.proxy import removeAllProxies
from persistent.dict import PersistentDict
from zope.component import getUtility

# jz modules
from interfaces import IStaticAnnotationCache, IAnnotationCache


# constant keys
default_key = "jz.cache.default"
static_cache_key = "jz.cache.static"
dynamic_cache_key = "jz.cache.dynamic"
empty_key_marker = object() # Random static marker for a default key parameter, which never corolates to any existing key.


class annotationCache(object):
	__doc__ = IAnnotationCache.__doc__

	implements(IAnnotationCache)

	def _getObjectCache(self, ob):
		"""Return the annotation containing the cache."""

		annotations = IAnnotations(removeAllProxies(ob))
		try:
			return annotations[dynamic_cache_key]
		except KeyError:
			cache = annotations[dynamic_cache_key] = {}
			return cache

	def invalidate(self, ob, key=empty_key_marker):
		"""Invalidate single object."""

		cache = self._getObjectCache(ob)
		if key is empty_key_marker:
			for key in cache.keys():
				del cache[key]
		else:
			del cache[key]

	def invalidateRecursive(self, ob, key=empty_key_marker):
		"""See jz.cache.interfaces.IAnnotationCache"""

		self.invalidate(ob, key)
		for child in ob.values():
			self.invalidateRecursive(child, key)

	def invalidateAll(self):
		"""Invalidate all from root."""

		raise NotImplemented

	def query(self, ob, key=default_key, default=None):
		cache = self._getObjectCache(ob)
		try:
			return cache[key]
		except KeyError:
			return default

	def set(self, data, ob, key=default_key):
		cache = self._getObjectCache(ob)
		cache[key] = data

AnnotationCache = annotationCache()


class staticAnnotationCache(annotationCache):
	__doc__ = IStaticAnnotationCache.__doc__

	implements(IStaticAnnotationCache)

	def _getObjectCache(self, ob):
		annotations = IAnnotations(removeAllProxies(ob))
		try:
			return annotations[static_cache_key]
		except KeyError:
			cache = annotations[static_cache_key] = PersistentDict()
			return cache

StaticAnnotationCache = staticAnnotationCache()


def ClearAnnotationCache(ob, event):
	"""Clear cache saved in annotations."""

	getUtility(IAnnotationCache).invalidate(ob)
	getUtility(IStaticAnnotationCache).invalidate(ob)