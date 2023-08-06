from docbook2sla import DocBook2Sla
d2s = DocBook2Sla()

print "===================================="
print " Test Article                       "
print "===================================="

print "=== test with named output files ==="
print d2s.create('tests/data/xml/article+id.xml',\
                 'tests/data/scribus/clean134.sla',\
                 output_filename='tests/data/output/create_output.sla')
print d2s.syncronize('tests/data/xml/article-1+id.xml',\
                     'tests/data/output/create_output.sla',\
                     output_filename='tests/data/output/syncronize_output.sla')

print "=== test with unnamed output files ==="
print d2s.create('tests/data/xml/article+id.xml',\
                 'tests/data/scribus/clean134.sla')
print d2s.syncronize('tests/data/xml/article-1+id.xml',\
                     'tests/data/output/create_output.sla')

print "===================================="
print " Test Book                          "
print "===================================="

print "=== test with named output files ==="
print d2s.create('tests/data/xml/article+id.xml',\
                 'tests/data/scribus/clean134.sla',\
                 output_filename='tests/data/output/create_output.sla')
print d2s.syncronize('tests/data/xml/article-1+id.xml',\
                     'tests/data/output/create_output.sla',\
                     output_filename='tests/data/output/syncronize_output.sla')

print "=== test with unnamed output files ==="
print d2s.create('tests/data/xml/article+id.xml',\
                 'tests/data/scribus/clean134.sla')
print d2s.syncronize('tests/data/xml/article-1+id.xml',\
                     'tests/data/output/create_output.sla')
