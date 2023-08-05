from zope.interface import Interface

class IDocBook2Sla(Interface):

    def convert(docbook_filename, scribus_filename):
        """ Merge a DocBook and a Scribus file (stored on the filesystem) to some output format.
            Returns the filename of the output file.
        """
