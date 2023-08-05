"""$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/durus/logger.py $
$Id: logger.py 1475 2005-12-01 17:36:40Z mscott $
"""

import sys
from logging import getLogger, StreamHandler, Formatter, INFO

logger = getLogger('durus')
log = logger.log

def direct_output(file):
    logger.handlers[:] = []
    handler = StreamHandler(file)
    handler.setFormatter(Formatter("%(message)s"))
    logger.addHandler(handler)
    logger.propagate = False
    logger.setLevel(INFO)
    if file is sys.__stderr__:
        return
    if sys.stdout is sys.__stdout__:
        sys.stdout = file
    else:
        pass
##         log(100, "sys.stdout already customized.")
    if sys.stderr is sys.__stderr__:
        sys.stderr = file
    else:
        pass
##         log(100, "sys.stderr already customized.")

if not logger.handlers:
    direct_output(sys.stderr)

def is_logging(level):
    return logger.getEffectiveLevel() <= level

