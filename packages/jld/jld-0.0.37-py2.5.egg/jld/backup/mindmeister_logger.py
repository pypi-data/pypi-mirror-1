#!/usr/bin/env python
"""
    MinMeister Logger
    @author: Jean-Lou Dupont
"""

__author__  = "Jean-Lou Dupont"
__version__ = "$Id: mindmeister_logger.py 729 2008-12-11 18:30:12Z jeanlou.dupont $"

import logging
import logging.handlers

# ==============================================
# ==============================================

def Logger(console_quiet = False, syslog_address = '/dev/log/mm.log'):
    """ Builds a Logger
        By default, outputs to stdout & syslog
        
        @param console_quiet: if True, disables logging to stdout
        @param syslog_address: the address to use for syslog
    """
    logging.basicConfig(level=logging.DEBUG,
                        format="%(asctime)s %(name)-12s %(levelname)-8s: %(message)s ",
                        datefmt='%y-%m-%d %H:%M'
                        )
    
    hconsole = logging.StreamHandler()
    hsyslog  = logging.handlers.SysLogHandler( address=syslog_address )
    
    # ===
    #formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
    #hconsole.setFormatter(formatter)
    #hsyslog.setFormatter(formatter)
    
    # ===
    loggr = logging.getLogger('')
    loggr.addHandler(hconsole)
    loggr.addHandler(hsyslog)
    
    return loggr

# ==============================================
# ==============================================

if __name__ == "__main__":
    """ Tests
    """
    log = Logger()
    log.info('test')
    