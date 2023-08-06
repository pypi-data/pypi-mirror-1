#!C:\Python25\python.exe
""" A simple preprocessor based on the Mako template engine
    @author: Jean-Lou Dupont
"""

__author__  = "Jean-Lou Dupont"
__version__ = "$Id: pypre.py 795 2009-01-13 19:42:53Z JeanLou.Dupont $"

import os
from optparse import OptionParser

import jld.template as tpl

_options =[]

_usage = """%prog [options] input_file   

Preprocessor based on the Mako template engine
version $LastChangeRevision$ by Jean-Lou Dupont
"""


def main():
    parser = OptionParser( usage=_usage )
    for o in _options:
        parser.add_option( o['o1'], 
                           dest=o['var'], 
                           action=o['action'], 
                           default=o['default'] )
    
    (options,args) = parser.parse_args()

    if len(args) < 1:
        print "Error: not enough arguments"
        exit(0)

    input  = args[0]
    
    if (not os.path.isfile(input)):
        print "Error: invalid input_file parameter"
        exit(0)
    
    try:    
        template = tpl.Tpl( input )
        result = template.render()
    except Exception,e:
        print "Error: template processing failed [%s]" % e
        exit(0)
        
    print result
    
# ==============================================
# ==============================================

if __name__ == "__main__":
    main()