#from lymon.core import Tag, Serialize, HTML, Document
#from lymon.view import Selector

#from tw.api import Widget, WidgetsList
#from tw.forms import TableForm
#from tw.forms.fields import TextField, SubmitButton
#from lymon.tw import Site

## Initialization

#class TestForm(TableForm):
#	class fields(WidgetsList):
#		testWidget1 = TextField(id='testWidget1', default = 'testWidget 1')
#		testWidget2 = TextField(id='testWidget2', default = 'testWidget 2') 

#class TestWidgetList(WidgetsList):
#	testWidget = Widget(template ="""<p> Test Widget </p>""")
#	testForm = TestForm()
#	
#html = Document()
#html.dic(slot='a.b.c', group = TestWidgetList())

##print html(render=True)

#site = Site(document= html())

#print site.display()

