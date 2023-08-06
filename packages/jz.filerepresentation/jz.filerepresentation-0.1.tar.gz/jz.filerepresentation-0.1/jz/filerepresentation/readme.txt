jz.filerepresentation:

This is an extended (Read|Write)Directory implementation.
It tries to make sure object names in a directory listing have the correct extension according to their types at all time. Any class that wishes to have it's file representation have an extension must implement an adapter to IFileName.

	>>> from tests.sample import Sample
	>>> from interfaces import IFileName
	>>> from zope.interface import implements

Implement an IFileName adapter for the Sample class

	>>> class SampleFileName(object):
	...		implements(IFileName)
	...
	...		def __init__(self, context):
	...			self.context = context
	...
	...		@property
	...		def name(self):
	...			return self.context.name
	...
	...		extension = ".sample"
	...
	...		@property
	...		def full(self):
	...			return ' '.join((self.name, self.extension,))
