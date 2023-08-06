from lymon.core import Document
from lymon.tw import Site
from time import time
from tw.api import Widget

c = Widget('c')
d = Widget('d', template="<p>ooo</p>")

i = time()

f = lambda: 'moe'

html = Document()
html.div(slot='a.b.c', attrs={'class': 'foo_class'})
html.a(slot='a.b.d', attrs={'class': 'foo_class'}, widgets=[(c, {'x':f(), 'y': f()}), d])
html.h3(slot='a.c.b', id=False, attrs={'class': 'foo_class'}, widgets=[c, d], html='foo')
html.h3(slot='a.c.t', id=False, attrs={'class': 'foo_class'}, widgets=[c, d], html='foo')
f = time()

print html(render=True)


site = Site(document=html())

print site.display()




print 'Render Time: %s' %(f-i)


