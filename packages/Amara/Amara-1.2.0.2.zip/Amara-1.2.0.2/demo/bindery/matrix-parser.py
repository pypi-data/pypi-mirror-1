#Convert a simple, matrix-like XML format to a Python data structure
DOC = """\
<matrix>
<a><b>x1</b><c>y1</c></a>
<a><b>x2</b><c>y2</c></a>
<a><b>x3</b><c>y3</c></a>
</matrix>
"""

from amara import binderytools

matrix = []
for row in binderytools.pushbind(u'a', string=DOC):
    matrix.append((unicode(row.b), unicode(row.c)))

print matrix


matrix = []
for row in binderytools.pushbind(u'a', string=DOC):
    matrix.append(tuple([ unicode(e) for e in row.xml_xpath(u'*') ]))

print matrix

