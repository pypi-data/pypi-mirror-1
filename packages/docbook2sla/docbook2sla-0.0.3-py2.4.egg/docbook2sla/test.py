from docbook2sla import DocBook2Sla
d2s = DocBook2Sla('tests/data/xml/content.xml', 'tests/data/scribus/clean134.sla')
print d2s.convert()

