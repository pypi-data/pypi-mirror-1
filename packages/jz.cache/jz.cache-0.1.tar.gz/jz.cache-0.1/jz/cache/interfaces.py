# zope modules
from zope.app.cache.interfaces import ICache


# Generic doc tests for all cache interfaces
# interface specific tests in class __doc__s
generic_doctest="""

	Setup some sample content:
	>>> content = root['sample'] = Content()

	Set some cached data on the content:
	>>> cache.set('some cached data', content)

	Get the cached data:
	>>> cache.query(content)
	'some cached data'

	Now with a non-default key:
	>>> cache.set('special data cached', content, key='content.special')
	>>> cache.query(content, key='content.special')
	'special data cached'

	"""


class IAnnotationCache(ICache):
	"""Cache utility. Cache is stored in annotations.

	Non-persistent cache.

	Test setup:
	>>> from zope.component import getUtility
	>>> cache = getUtility(IAnnotationCache)
	"""

	__doc__ = __doc__ + generic_doctest


	def invalidateRecursive(ob, key):
		"""Invalidate cache for ob and all children."""


class IStaticAnnotationCache(IAnnotationCache):
	"""Cache utility. Cache is stored statically in annotations.

	Persistent cache.

	Test setup:
	>>> from zope.component import getUtility
	>>> cache = getUtility(IStaticAnnotationCache)
	"""

	__doc__ = __doc__ + generic_doctest