#
# Copyright Laureano Arcanio 2008
# Released under the MIT License
# laureano.arcanio@gmail.com
#

__all__ = ['MetaTag']

__default__ = dict(	slot = '',
					tag = 'div',
					attrs = {},
					name ='__default__',
					html = '',
					id = True,
					widgets = False)

class MetaTag(type):
	"""
	Metaclass extending type.
	"""
	def __new__(meta, name , bases, dct):
		# Deletes method and attributes containing "_"
		for key, value in dct.items():
			if '_' in key:
				dct.pop(key)
		items = dct.copy()
		def __init__(cls, **kw):
			if not 'name' in kw.keys():
				kw.update({'name':name})
			default = __default__.copy()
			default.update(items)
			default.update(kw)
		 	if not '#' in default['slot']:
		 		default['slot'] += "#%s" % name
			if default['id']:
				if not 'id' in default['attrs'].keys():
					slot = default['slot'][:default['slot'].index('#')]
					if slot:
						id = slot.split('.')[-1]
						t = default['attrs'].copy()
						t.update({'id': id})
						default['attrs'] = t.copy()
		 	cls.update(default)
		dct.update({'__init__':__init__})
		return  type.__new__(meta,name,bases,dct)





#class MetaHTML(type):
#	def __new__(meta, name , bases, dct):
#		# Deletes methos and attributes containing "_"
#		items = []
#		for key, value in dct.items():
#			if '_' in key:
#				dct.pop(key)
#				
#		# Set default keys and values if they not exist.
#		
#		#items = filter(lambda k: not "_" in k, list(dct.values()))  
#		items = [tag() for tag in dct.values()]
#		
#		#items = list(dct.values())
#		def __init__(self, items=items): 
#			self.extend(items)
#		dct.update({'__slots__':[], '__init__':__init__})
#		return type.__new__(meta,name,bases,dct)

#class MetaContext(type):
#	"""
#	Metaclas for Tag Construction.
#	"""
#	def __new__(cls, name, bases, dct):
#		def __init__(self): pass
#		def __getattr__(self, key):
#			if '_' not in key:
#				def func(**kw):
#					#tagName = 'tag%s' % len(self.tags)
#					kw.update({'tag':key, 'name': name})
#					#return Tag(kw)
#					self.tags.append(Tag(kw))
#				return func
#			else:
#				try: 
#					return getattr(self, key)
#				except Exception, e:
#					print "Error: %s" % (e)
#		dct.update({'__init__': __init__, '__getattr__': __getattr__, 'tags':[]})
#		return type.__new__(cls, name, bases, dct)

