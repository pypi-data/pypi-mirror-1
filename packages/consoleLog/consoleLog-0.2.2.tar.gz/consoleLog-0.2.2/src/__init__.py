# -*- coding: utf-8 -*-
# 
#  __init__.py
#  consoleLog
#  
#  Created by Lars Yencken on 2008-06-12.
#  Copyright 2008-06-12 Lars Yencken. All rights reserved.
# 

__all__ = [
        'consoleLog',
        'io',
        'progressBar',
        'shell',
    ]

#----------------------------------------------------------------------------#

import consoleLog
import progressBar
from progressBar import withProgress

#----------------------------------------------------------------------------#

# Provide a default logging object 
default = consoleLog.ConsoleLogger()

#----------------------------------------------------------------------------#

def demo():
    import time
    sl = time.sleep
    log = consoleLog.ConsoleLogger()

    log.start('Starting logger demo')
    log.log('Performing some initialisation')
    sl(1.0)

    log.start('Serious processing with substeps')
    log.log('Substep 1')
    sl(1.0)
    log.log('Substep 2')
    sl(1.0)
    log.log('Substep 3 with progress ', newLine=False)
    for i in withProgress(xrange(100)):
        sl(0.1)
    log.finish('Completed ok')

    log.log('Postprocessing step')
    sl(1.0)
    log.finish()
