#
# Copyright Laureano Arcanio 2008
# Released under the MIT License
# laureano.arcanio@gmail.com
#

__all__ = ['Serialize']


serializer_defaults = dict(
	instantation_sintax = "${%s['%s'](%s)}",	# ('widget', name, parameters, html )
	widget_params = {'displays_on': 'genshi'},	# Set parameters at instantation time  
	engine_name = 'genshi',						# Set tamplate engine
	force_id = True)	

class Serialize(object):
	"""
	tree = [('x',[])]
	List of tuples, (name, children)
	context = [of Tag]
	"""
	tree = []
	def __init__(self, context=[], defaults=serializer_defaults):
		self.defaults = defaults
		self.context = context
		slots = [k['slot'] for k in context if "_" not in k['name']]
		self.tags = dict([(tag['name'], tag) for tag in self.context])
		display = [slot.split('.')[-1] for slot in slots]
		if slots:
			self.makeTree(slots)
			self.template = self.render(tree=self.tree, display=display)

	def updateTree(self, slot='', tree=[]):
		"""
		Adds a slot to a given tree
		slot = 'a.b.c'
		"""
		if type(slot) == str:
			slot = slot.split('.')
		t = tree
		while slot:
			head = slot.pop(0)
			# branches hold all branch of the of the current node
			branches = [branch[0].split('#').pop(0) for branch in tree]
			if head in branches:
				# Index if the matching head to tree
				index = branches.index(head)
				tree = tree[index][1]
			else:
				tree.append((head,[]))
				tree = tree[-1][1]
		return t
		
	def makeTree(self, slots=[]):
		"""
		Build a tree from a given Slot List
		"""
		if type(slots) == list:
			tree = []
			while slots:
				slot = slots.pop(0)
				tree = self.updateTree(slot, tree)
			self.tree = tree
		return self.tree
		
	def render(self, tree=[()], deep=0, display=[] ):
		"""
		Render the template from given Tree.
		[('a',[])]
		"""
		branches = [branch for branch in tree]
		template = ""
		while branches:
			branch = branches.pop(0)
			head = branch[0]
			first = branch[1]
			# Call openTag for a open definition
			template += (deep * "\t") + self.openTag(head)
			if head in display:
				# Inject widgets and parameters for instantation
				template += self.content(head, (deep * "\t") + "\t")		
			deep += 1
			# Call endTag for a end definition
			template = template % (self.render(first, deep, display))
			deep -= 1
			template += ((deep) * "\t") + self.endTag(head)
		return template
			
	def openTag(self, tag=""):
		"""
		HTML open tag renderization
		"""
		if "#" in tag:
			tagName = tag.split('#')[1]
			tag = tag.split('#')[0]
			tagDef = self.tags[tagName]
		else:
			tagDef = self.tags['__default__']
		string =''
		for attr, value in tagDef['attrs'].items():
			string += """%s="%s" """ % (attr, value)
		
		if tagDef['id'] and 'id' not in tagDef['attrs'].keys():
			string += """%s="%s" """ % ('id', tag)
		
		openTag = "<%s %s>\n" % (tagDef['tag'], string) + "%s"
		return openTag
		
	def content(self, tag="", deep=''):
		"""
		Widgets instantation and parametrization template,
		"""
		gettedTag = self.getTag(tag)
		if gettedTag:
			tagName = gettedTag['name']
		tag = tag.split('#')[0]
		
		widget_params = list(self.defaults['widget_params'].iteritems())
		default_params = ""
		
		for param, value in widget_params:
			default_params += '%s="%s",' % (param, value)

		instantation_sintax = self.defaults['instantation_sintax']
		widgets = gettedTag['widgets']
		instantation = ''
		if widgets:
			for widget in widgets:
				if (type(widget) == type(())):
					params = widget[1]
					if params:
						params_string = ''
						for param, value in params.iteritems():
							value_string = "calls['%s']['%s']" % (widget[0].id, param)
							if param:
								params_string += '%s=%s,' % (param, value_string)
							else:
								value_string = "calls['%s'][%s]" % (widget[0].id, param)
								params_string += '%s,' % (value_string)
							instantation_params = params_string + default_params
					_widget = widget[0]
				else:
					instantation_params = default_params
					_widget = widget
				instantation += deep + (instantation_sintax + "\n") % ('widgets', _widget.id, instantation_params)
		instantation += deep + '%s\n' % gettedTag['html']
		return (instantation)

	def endTag(self, tag=""):
		"""
		HTML end tag renderization
		"""
		endTag = "</div>\n"
		if "#" in tag:
			tagName = tag.split('#')[1]
			tag = tag.split('#')[0]
			tagDef = self.tags[tagName]
		else:
			tagDef = self.tags['__default__']
		endTag = "</%s>\n" % tagDef['tag']
		return endTag
	
	def getTag(self, tag=''):
		# If the tag is defined return it, else None
		if '#' in tag:
			f = lambda tag: tag[(tag.index('#') + 1):]
			return self.tags[f(tag)]
		else:
			return None

