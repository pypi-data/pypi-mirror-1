# zope modules
from zope.interface import Interface
from zope.schema import TextLine
from zope.i18nmessageid import MessageFactory


_ = MessageFactory("jz.filerepresentation")


class IFileName(Interface):
	"""File name."""

	name = TextLine(
		title=_("Base file name"),
	)

	extension = TextLine(
		title=_("Extension"),
		description=_("File name extension (without separator)"),
		required=False,
	)

	full = TextLine(
		title=_("Full file name"),
		readonly=True,
	)