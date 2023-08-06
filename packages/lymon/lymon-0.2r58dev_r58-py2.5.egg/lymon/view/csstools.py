#
# Copyright Laureano Arcanio 2008
# Released under the MIT License
# laureano.arcanio@gmail.com
#

__all__ = ['Selector']

from lymon.core import Tag
from selectors import W3CTypes

class Selector(object):
	"""
	Class to build CSS selectors for a given Tag
	"""
	def __init__(self, tag={}, context = []):
		self.tag = tag.copy()
		self.context = context[:]
		self.matched = dict(self.match(tag=self.tag, context=self.context))
		
	def match(self, tag={}, context=[]):
		"""
		if slot = "a.b.c" -> Returns Tuples of [(a, tag(a))]
		"""
		matched = [()]
		if tag and context:
			# Whohoo nice unreadable list comphresions
			f = lambda t: t[:t.index('#')] != ''
			slots = [tag['slot'][:tag['slot'].index('#')] for tag in context if f(tag['slot'])]
			slot = tag['slot'][:tag['slot'].index('#')].split('.')
			t = ''
			matched = []
			for name in slot:
				t += name
				if t in slots:
					index = slots.index(t) + 1
					matched.append((name, context[index]))
				t += '.'
		return matched

	def tagAttrs(self):
		"""
		Reurn Tags attributes
		"""
		tag = self.tag
		matched = self.matched
		tags = tag['slot'][:tag['slot'].index('#')].split('.')
		attrs = []
		for name in tags:
			if name in matched.keys():
				attrs.append((name, matched[name]))
			else:
				attrs.append((name,Tag(slot=name)))
		return attrs

	def build(self, **kw):
		"""
		From [('tag', 'attrs')] builds a CSS selector
		"""
		selectors = W3CTypes()
		attrs = self.tagAttrs()
		string = ''
		for tag in attrs:
			string += "%s " % selectors.ById(tag[1])
		return string




	
	

