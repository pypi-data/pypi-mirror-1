from docbook2sla import DocBook2Sla
d2s = DocBook2Sla()
print d2s.create('tests/data/xml/content.xml',\
                 'tests/data/scribus/clean134.sla',\
                 output_filename='tests/data/output/create_output.sla')
print d2s.syncronize('tests/data/xml/content-1.xml',\
                     'tests/data/output/create_output.sla',\
                     'tests/data/output/syncronize_output.sla')
