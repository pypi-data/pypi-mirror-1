#
# Copyright Laureano Arcanio 2008
# Released under the MIT License
# laureano.arcanio@gmail.com
#

__all__ = ['Tag', '__default__', 'Document']

from metatag import MetaTag
from serializer import Serialize

class Tag(dict):
	"""
	Sintactic suggar for declaring an HTML Tag.
	"""
	__metaclass__ = MetaTag
	
# Default Tag
__default__ = Tag

class Document(object):
	"""
	Class for building HTML documents
	html = Document()
	html.div(slot = 'site.top.a1', tag = 'div',id = True, attrs = {'class':'a1', 'id': 'TagConId'})
	html.h1(slot = 'site.top.a2', tag = 'h1',id = False, attrs = {'class':'a2'})
	html(render=True) # Return the generated template
	"""
	tags = []
	template = """"""
	def __init__(self):
		self.context=[]
		self.template=""""""
		self.context.append(Tag(name = '__default__'))

	def __getattr__(self, key):
		"""
		Intercept method calls and create a tag with method name and parameters
		document = Document()
		document.div(slot='a.b.c')
		"""
		if '_' not in key:
			def func(**kw):
				tagName = 'tag%s' % len(self.context)
				kw.update({'tag':key,'name': tagName})
				# Monkey Patched ? ( not really )
				kw['slot'] += "#%s" % tagName
				default = Tag(**kw)

				self.context.append(default)
			return func
		else:
			try: 
				return getattr(self, key)
			except Exception, e:
				print "Error: %s" % (e)
				
	def __call__(self, render=False):
		"""
		Render the template on a Class call:
		document(render=True) 	-> Returns Rendered HTML
		document() 				-> Returns a document Object
		"""
		if render:
			if len(self.context) > 1:
				self.template = Serialize(context=self.context).template
				self.widgets, self.calls = _widgets(self.context)
				return self.template
			else:
				return ""
		else:
			self.template = Serialize(context=self.context).template
			self.widgets, self.calls = _widgets(self.context)
			return self
			
	def inherit(self, document=None):
		"""
		x.inherit(y)
		X New document, Y Parent document
		X inherits from Y. ( X tags take precedece over Y )
		"""
		thisContext = self.context[:]
		self.context = document.context[:]
		# Remove tag name identifier in slot: slot='a.b.c#tag1' -->  slot='a.b.c' 
		clean = lambda tag: tag['slot'][:tag['slot'].index('#')]
		bySlots = [clean(tag) for tag in self.context]
		for tag in thisContext:
			if clean(tag) in bySlots:
			# If the Tag exists, edit it with new one
				name = self.context[bySlots.index(clean(tag))]['name']
				slot = clean(tag) + ("#%s" % name)
				self.context[bySlots.index(clean(tag))] = tag.copy()
				self.context[bySlots.index(clean(tag))]['name'] = name
				self.context[bySlots.index(clean(tag))]['slot'] = slot
			else:
			# If tag doesn't exist, append a new and change name and slot 
				index = len(self.context)
				name = tag['name'] = "tag%s" % index
				tag['slot'] = clean(tag) + ("#%s" % name)
				self.context.append(tag)

def _widgets(context):
	"""
	Builds a dict of Widgets , to be passed to serializer
	2 cases:	widgets = [widget1,...widgetN]
				widgets = [(widget1, {'param':'value', 'param2', function()}), ... , widgetN]
	"""
	widgets_context = []
	calls_context = []
	for tag in context:
		widgets = tag['widgets']
		if widgets:
			for widget in widgets:
				if (type(widget) != type(())):
					widgets_context.append((widget.id, widget))
				else:
					widgets_context.append((widget[0].id, widget[0]))
					calls_context.append((widget[0].id, widget[1]))
	calls_context = dict(calls_context)
	widgets_context = dict(widgets_context)
	return widgets_context, calls_context
	


	
	
