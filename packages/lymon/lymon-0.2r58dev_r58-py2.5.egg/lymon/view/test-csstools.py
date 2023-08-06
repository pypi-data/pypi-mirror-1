from lymon.core import *
from time import time

start = time()

html = Document()
#html.div(slot='a')
html.div(slot='a.b', attrs={'class': 'classB'})
html.div(slot='d.b', id=False)
html.div(slot='a.c')
html.h6(slot='a.b.c', attrs={'id': 'title'})

tag = html.context[-1]


#print html.tags

s = Selector(tag=tag, context=html.context)

print s.build()

end = time()

print "Build time: %s" % (end - start)

