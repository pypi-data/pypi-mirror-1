jz.cache:

Cache utilities and decorators.

The utilities can be used by getting them with getUtility, or using the decorators in the property module.

	>>> from zope.interface import implements
	>>> from zope.annotation.interfaces import IAttributeAnnotatable
	>>> from jz.cache.property import cachedProperty, cachedFunction

	>>> class Num(object):
	...		implements(IAttributeAnnotatable)
	...
	...		def __init__(self, value):
	...			self.value = value
	...
	...		@cachedProperty("num.square")
	...		def square(self):
	...			return self.value ** 2
	...
	...		@cachedFunction("num.add")
	...		def add(self, other):
	...			return self.value + other

	>>> num = Num(2)
	>>> num.square
	4
	>>> num.add(3)
	5

	Change the value:
	>>> num.value = 3

	But the cached result remains:
	>>> num.square
	4

	Same for the cached function:
	>>> num.add(3)
	5

	Only after invalidation:
	>>> from zope.component import getUtility
	>>> from jz.cache.interfaces import IAnnotationCache
	>>> cache = getUtility(IAnnotationCache)
	>>> cache.invalidate(num)

	Is the new result calculated:
	>>> num.square
	9
	>>> num.add(3)
	6