""" Pretty Printer
    @author: Jean-Lou Dupont
"""

__author__  = "Jean-Lou Dupont"
__version__ = "$Id: printer.py 708 2008-12-04 13:40:35Z JeanLou.Dupont $"

class BasePrettyPrinter(object):
    """Generic Pretty Printer"""

    def __init__(self):
        self.tbl_hdr = None #cached table header

    def header(self):
        """Prints a header"""
        
    def table_header(self, tpl_item = None):
        """Prints a table header"""
    
    def footer(self):
        """Prints a footer"""
    
    def line(self, entry):
        """Prints one line"""
    
    def run(self, list, page_len = 20, repeat_table_header = True):
        """Default (basic) printer implementation"""
        self.header()
        count = 0
        for item in list:
            if (not count):
                count = page_len
                self.table_header( item )
            self.line(item)
            count = count - 1
        self.footer()

# ==================================================================

class SimplePrettyPrinter(BasePrettyPrinter):
    """Simple Printer which uses stdout"""

    def table_header(self, item_tpl):
        """Prints a table header"""
        if (self.tbl_hdr):
            print self.tbl_hdr
            return
        
        self.tbl_hdr = ''
        keys = item_tpl.keys()
        for key in keys:
            self.tbl_hdr = self.tbl_hdr + str(key) + ' , '

        self.tbl_hdr = self.tbl_hdr.rstrip(" ,")
        print self.tbl_hdr
        print "--" 
    
    def line(self, entry):
        """Prints one line"""
        result = ''
        for item in entry:
            result = result + entry[item] + ' , '
            
        print result.rstrip(' ,')


# ==============================================
# ==============================================

if __name__ == "__main__":
    """ Tests
    """
    liste = [
        { 'id': '1', 'title':'title1' },
        { 'id': '2', 'title':'title2' },        
    ]

    printer = SimplePrettyPrinter()
    
    printer.run(liste)
