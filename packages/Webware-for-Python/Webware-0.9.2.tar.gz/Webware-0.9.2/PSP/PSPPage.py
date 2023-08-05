"""Default base class for PSP pages.

This class is intended to be used in the future as the default base class
for PSP pages in the event that some special processing is needed.
Right now, no special processing is needed, so the default base class
for PSP pages is the standard WebKit Page.

"""

from WebKit.Page import Page


class PSPPage(Page):

	def __init__(self):
		# self.parent = str(self.__class__.__bases__[0]).split('.')[1]
		#print self.parent
		self.parent = Page
		self.parent.__init__(self)

	def awake(self, trans):
		self.parent.awake(self, trans)
		self.out = trans.response()

