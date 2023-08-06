# zope modules
from zope.interface import implements
from zope.traversing.api import getName

# python modules
import os

# jz modules
from interfaces import IFileName
from jz.common import SimpleAdapter


class FileName(SimpleAdapter):
	"""Generic base class for filename adapter.

	This implementation assumes the object is locatable.

	Example:

		>>> from jz.testing.sample import Content
		>>> content = root['content'] = Content()

	Use the generic adapter :

		>>> filename = FileName(content)

	Get the file's name :

		>>> filename.name
		u'content'

	And extension, which is empty by default :

		>>> filename.extension
		u''

	And full name, which in the case of the default adapter consists of only the name :

		>>> filename.full
		u'content'

	Now we'll add an adapter which does return an extension :

		>>> class ExtFileName(FileName):
		...		extension = u"ext"

		>>> extfilename = ExtFileName(content)
		>>> extfilename.extension
		u'ext'

		>>> extfilename.full
		u'content.ext'

	"""

	implements(IFileName)

	@property
	def name(self):
		return getName(self.context)

	@property
	def extension(self):
		# No extension returned by default.
		return u''

	@property
	def full(self):
		if len(self.extension) != 0:
			return u'%s%s%s' % (self.name, os.extsep, self.extension,)
		else:
			return self.name