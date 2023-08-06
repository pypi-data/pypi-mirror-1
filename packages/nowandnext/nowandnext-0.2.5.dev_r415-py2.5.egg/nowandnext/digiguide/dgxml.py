from elementtree.ElementTree import Element, SubElement, ElementTree as ET

class dgxml( object ):
    def __init__(self):
        self.oldestStart = None
        self.newestEnd = None
        self.itemCount = 0
        self._xml = Element()

    def addItem( self, item ):
        """
        Add an item to the digiguide schedule
        """


    def dump( self, file ):
        """
        Write out the digiguide XML to a file.
        """
        file.write( self.dumps() )

    def dumps( self ):
        return
