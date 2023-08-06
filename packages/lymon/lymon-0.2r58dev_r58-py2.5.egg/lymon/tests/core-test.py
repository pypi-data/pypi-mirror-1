#
# Copyright Laureano Arcanio 2008
# Released under the MIT License
# laureano.arcanio@gmail.com
#

from unittest import TestCase

from lymon.core import Tag, Serialize, Document
from lymon.view import Selector

from tw.api import Widget, WidgetsList
from tw.forms import TableForm
from tw.forms.fields import TextField, SubmitButton

# Initialization

class TestForm(TableForm):
	class fields(WidgetsList):
		testWidget1 = TextField(id='testWidget1', default = 'testWidget 1')
		testWidget2 = TextField(id='testWidget2', default = 'testWidget 2') 

class TestWidgetList(WidgetsList):
	testWidget = Widget(template ="""<p> Test Widget </p>""")
	testForm = TestForm()

def returnTag(slot_test='site.form', tag_test= 'div', attrs_test= {'class':'siteheader'}, widgets_test= TestWidgetList()):
	class TagA(Tag):
		slot = slot_test
		tag = tag_test
		attrs = attrs_test
		widgets = widgets_test
	return TagA()

# Tests

class Tag_Test(TestCase):
	def runTest(self):
		tag = returnTag('site.form','div',{'class':'siteheader'},TestWidgetList())
		match = {'slot': 'site.form#TagA', 'tag': 'div', 'name': 'TagA', 'widgets': [Widget('testWidget', children=[], **{'template': '<p> Test Widget </p>'}), TestForm('testForm', children=[TextField('testWidget1', children=[], **{'default': 'testWidget 1'}), TextField('testWidget2', children=[], **{'default': 'testWidget 2'}), SubmitButton('submit', children=[], **{'default': 'Submit', 'label_text': ''})], **{})], 'id': True, 'html': '', 'attrs': {'class': 'siteheader', 'id': 'form'}}
		
		self.assertEqual(tag, match)
		
# Tests the HTML class, declare 2 Tags and use inheritance. Compare the 2 sintax methods
class Documents_Test(TestCase):
	def runTest(self):
		# New Style
		newSintax = Document()
		newSintax.div(slot = 'site.top.a1', attrs = {'class':'a1', 'id': 'TagConId'})
		newSintax.h1(slot = 'site.top.a2', id = False, attrs = {'class':'a2'})

		newSintax.span(slot = 'site.bottom.wg', id = True, attrs = {'class':'widgets_cont'}, html='<p> Hello World </p>', widgets=[(TestForm(), {'values':{'testWidget1': 'some_value'}})] )
		
		
		template = '<div id="site" >\n\t<div id="top" >\n\t\t<div class="a1" id="TagConId" >\n\t\t\t\n\t\t</div>\n\t\t<h1 class="a2" >\n\t\t\t\n\t\t</h1>\n\t</div>\n\t<div id="bottom" >\n\t\t<span class="widgets_cont" id="wg" >\n\t\t\t${widgets[\'None\'](values=calls[\'None\'][\'values\'],displays_on="genshi",)}\n\t\t\t<p> Hello World </p>\n\t\t</span>\n\t</div>\n</div>\n'
		
		self.assertEqual(newSintax(render=True), template ,"Wrong template rendering, new sintax !")

	 	#Test for the inheritance mechanism 

		newSintaxInherited = Document()
		newSintaxInherited.div(slot = 'site.top.a1.new', attrs = {'class':'inherited_class', 'id': 'some_is'}, html='<h1> This is inherited </h1>')
		newSintaxInherited.inherit(newSintax)
			
		template = '<div id="site" >\n\t<div id="top" >\n\t\t<div class="a1" id="TagConId" >\n\t\t\t<div class="inherited_class" id="some_is" >\n\t\t\t\t<h1> This is inherited </h1>\n\t\t\t</div>\n\t\t\t\n\t\t</div>\n\t\t<h1 class="a2" >\n\t\t\t\n\t\t</h1>\n\t</div>\n\t<div id="bottom" >\n\t\t<span class="widgets_cont" id="wg" >\n\t\t\t${widgets[\'None\'](values=calls[\'None\'][\'values\'],displays_on="genshi",)}\n\t\t\t<p> Hello World </p>\n\t\t</span>\n\t</div>\n</div>\n'	

		
		self.assertEqual(newSintaxInherited(render=True), template ,"Wrong template rendering, new sintax !")

#		
# Tests the Selector class.
class Selector_Test(TestCase):
	"""
	Test Selector module
	"""
	def runTest(self):
		# preparing the document
		html = Document()
		html.div(slot='a', attrs={'id': 'mainTag'})
		html.div(slot='a.b', attrs={'class': 'classB'})
		html.div(slot='a.c')
		html.h6(slot='a.b.c', attrs={'id': 'title'})
		# Tag to Match 
		tag = html.context[-1]
		s = Selector(tag=tag, context=html.context)
		# Matched to compare
		matched = s.build()
		
		compare = 'div#mainTag div#b h6#title '
		# Test
		self.assertEqual(matched, compare, "There is a problem matching tags !")
	

