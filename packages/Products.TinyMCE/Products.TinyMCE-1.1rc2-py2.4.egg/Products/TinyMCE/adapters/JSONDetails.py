from zope.interface import implements
from zope.component import adapts
from zope.component import getUtility
from Products.TinyMCE.libs import json
from Products.TinyMCE.interfaces.utility import ITinyMCE

from Products.TinyMCE.adapters.interfaces.JSONDetails import IJSONDetails
from Products.CMFCore.interfaces._content import IContentish, IFolderish
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from Products.CMFCore.utils import getToolByName
from Acquisition import aq_inner
from elementtree import HTMLTreeBuilder;
	
class JSONDetails(object):
	"""Return details of the current object in JSON"""
	implements(IJSONDetails)

	def __init__(self, context):
		"""Constructor"""
		self.context = context

	def getDetails(self):
		"""Returns the actual details"""

		utility = getUtility(ITinyMCE)
		anchor_meta_types = utility.containsanchors.split('\n')
		image_meta_types = utility.imageobjects.split('\n')

		results = {};
		results['title'] = self.context.Title()
		results['description'] = self.context.Description()

		if self.context.meta_type in image_meta_types:
			results['thumb'] = self.context.absolute_url() + "/image_thumb"
		else:
			results['thumb'] = ""

		if self.context.meta_type in anchor_meta_types:
			results['anchors'] = [];
			# content = '<html><head></head><body><a name="tildeancor"></a></body></html>'
			tree = HTMLTreeBuilder.TreeBuilder()
			tree.feed('<root>%s</root>' % self.context.getText())
			rootnode = tree.close()
			for x in rootnode.getiterator():
				if x.tag == "a":
					if "name" in x.keys():
						results['anchors'].append(x.attrib['name'])
		else:
			results['anchors'] = []

		return json.write(obj=results, escaped_forward_slash=True);
