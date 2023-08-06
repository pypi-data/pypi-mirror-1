#
# Copyright Laureano Arcanio 2008
# Released under the MIT License
# laureano.arcanio@gmail.com
#

__all__ = ['W3CTypes']

class W3CTypes(object):
	# format = '.'
	
	def Universal(self, tag={}):
		return '*'
		
	def ByType(self, tag={}):
		"""
		# rule for selecting by tag type
		"""
		selector = tag['tag']
		
		return selector
	
	def ById(self, tag={}):
		if 'id' in tag['attrs'].keys():
			tagType = tag['tag']
			id = tag['attrs']['id']
			selector = '%s#%s' % (tagType, id)
		else:
			selector = self.ByType(tag)
			print "Not Id for this Tag, Using a Type selector instead"
		return selector
