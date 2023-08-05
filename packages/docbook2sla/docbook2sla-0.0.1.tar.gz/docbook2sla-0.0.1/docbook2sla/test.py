from docbook2sla import DocBook2Sla
d2s = DocBook2Sla('xml/content.xml', 'scribus/clean134.sla')
print d2s.convert('xml/content.xml', 'scribus/clean134.sla')

