#
# Copyright Laureano Arcanio 2008
# Released under the MIT License
# laureano.arcanio@gmail.com
#

from tw.api import Widget

__all__ = ["Site"]

class Site(Widget):
	""" 
	A widget to Build a template on the fly based on Slot atributes of Grups of Widgets.
	It also build a Tree of the HTML structure. It can be used after instantation.
	Slots are positional attributes, like slot='header.logo.component' where each word must be unique.
	The last word in the ( separated by "." ) is the name of the Container for a grup of Widget.
	Take a look at the Grup Widget Definition for furter understanding.

	"""
	
	params = ['preTemplate', 'widgets', 'calls']
	
	calls ={}

	preTemplate = ""
	displays_on="genshi"
	engine_name = 'genshi'
	template = ""
	tree = {}
	
	def __init__(self,*k, **kw):
		super(Site, self).__init__(*k,**kw)
		self.document = kw['document']
		self.calls = self.document.calls
	
		params = [k for k in self.params]	

		self.params = frozenset(params)
		self.widgets = self.document.widgets
		preTemplate = self.document.template
		
		self.template = """<div xmlns:py="http://genshi.edgewall.org/" py:strip="">\n%s\n</div>""" % (preTemplate)
		




		
		
