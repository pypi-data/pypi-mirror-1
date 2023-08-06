# -*- coding: utf-8 -*-
# 
#  consoleLog.py
#  consoleLog
#  
#  Created by Lars Yencken on 2008-06-12.
#  Copyright 2008 Lars Yencken. All rights reserved.
# 

"""
A simple logging module which allows hierarchical logging without centralized
control.

>>> log = ConsoleLogger()
>>> log.start('ABC', nSteps=3)
ABC
>>> log.log('A')
├─ A
>>> log.log('B')
├─ B
>>> log.log('C')
└─ C
>>> log.finish()
"""

#----------------------------------------------------------------------------#

import sys
import codecs

_default_encoding = 'utf8'

#----------------------------------------------------------------------------#

class ConsoleLogger(object):
    """
    A console logging object, which can optionally be given an output stream
    which it prints to, defaulting to stdout.
    """
    def __init__(self, output=None, trim=78, encoding=_default_encoding):
        self.oStream = codecs.getwriter(encoding)(output or sys.stdout)
        self.logStack = []
        self.trim=trim

    def start(self, message, nSteps=None):
        """
        Starts a new hierarchical logging section. Every call to start() must
        be later matched by a call to finish().
        """
        self.log(message)
        self.logStack.append(_SectionPadding(nSteps=nSteps))
        return

    def log(self, message, newLine=True):
        """
        Logs a message, with an optional newline. The most common case for
        not using the newline is for subsequent use of a progress bar.
        """
        if self.logStack:
            padding = []
            for levelLogger in self.logStack[:-1]:
                padding.append(levelLogger.getIntermediatePadding())
            padding.append(self.logStack[-1].getCurrentPadding())
        else:
            padding = u''
        oLine = u'%s%s' % (u''.join(padding), message)
        if self.trim and len(oLine) > self.trim:
            oLine = oLine[:self.trim - 3] + u'...'
        self.oStream.write(oLine)
        if newLine:
            print >> self.oStream
        else:
            self.oStream.flush()
        return

    def finish(self, message="Done"):
        """
        Ends a hierarchical logging section which was previously created using
        start().
        """
        padding = []
        for levelLogger in self.logStack[:-1]:
            padding.append(levelLogger.getIntermediatePadding())
        last = self.logStack.pop()
        padding.append(last.getLastPadding())
        if last.needsFinish():
            print >> self.oStream, u"%s%s" % (u''.join(padding), message)
        return

#----------------------------------------------------------------------------#

class _SectionPadding(object):
    """
    A manager for the amount of padding needed for any given log line, as well
    as any embellishments needed to indicate hierarchy.
    """
    def __init__(self, nSteps=None):
        """Private constructor used internally."""
        self.nSteps = nSteps
        self.currentStep = 0

    def getIntermediatePadding(self):
        if self.currentStep == self.nSteps:
            return u'   '
        else:
            return u'│  '

    def getCurrentPadding(self):
        self.currentStep += 1
        if self.currentStep == self.nSteps:
            return u'└─ '
        else:
            return u'├─ '

    def needsFinish(self):
        return self.currentStep != self.nSteps

    def getLastPadding(self):
        return u'└─ '

#----------------------------------------------------------------------------#
