"""
    Jean-Lou Dupont's Python library
    
    Installation
    ============
      Use I{easy_install jld} to install this library.
    
    Command-Line Tools
    ==================
      The following tools will be installed as scripts:
       - pypre.py [preprocessor based on Mako]
       - nsvn.py  [nuke svn]
       - dlc.py   [delicious backup]
       - mm.py    [mindmeister backup]
       - glf.py   [gliffy backup]
    
    @author: Jean-Lou Dupont
"""

__author__  = "Jean-Lou Dupont"
__version__ = "0.0.35"
__email__   = "python@jldupont.com"
__url__     = "http://www.jldupont.com/"
__desc__    = """ Jean-Lou Dupont's Python Library - WEB API & command line tools"""
__doc_url__ = "http://www.jldupont.com/doc/lib/jld/"

#
# must be in reStructuredText format (see http://docutils.sf.net/)
#
__long_desc__ = """
Content
=======

This library contains the following utilities:
  
* MindMeister mindmaps Backup command line: for exporting mindmaps from MindMeister in FreeMind format
  * EventManager script interface
  
* Delicious API & Backup command line utility

* Gliffy API & Backup command line utility

* Command-Line tools

  * pypre   (preprocessor based on Mako, e.g. useful for pre-processing Apache config files)
  
  * nsvn    (nuke svn: removes svn directories, e.g. useful under Windows where .dot files are difficult to handle)
 
* Cross-platform registry (Windows: uses the win32 registry, Linux: uses a filesystem path)

"""
__dependencies__ = [] #listed throughout the individual modules

__classifiers__ = [
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'License :: Public Domain',
    'Programming Language :: Python',
    'Topic :: Software Development :: Libraries :: Python Modules',
    'Operating System :: Microsoft :: Windows',
    'Operating System :: POSIX',
    ]

