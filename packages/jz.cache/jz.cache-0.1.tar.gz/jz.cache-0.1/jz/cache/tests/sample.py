# zope modules
from zope.interface import implements
from persistent import Persistent
from zope.app.container.contained import Contained

# test modules
from isample import IContent


class Content(Persistent, Contained):
	implements(IContent)