# -*- coding: utf-8 -*-
# 
#  progressBar.py
#  consoleLog
#  
#  Created by Lars Yencken on 2008-06-12.
#  Copyright 2008-06-12 Lars Yencken. All rights reserved.
#

"""
A simple console progress bar, with support for iterator wrapping.
"""

#----------------------------------------------------------------------------#

import sys
import time

import io, shellColor

#----------------------------------------------------------------------------#

_currentBar = None

class IllegalNestingError(Exception):
    pass

def withProgress(seq, modValue=1, size=None, force=False):
    """
    A wrapper for sequence which adds a progress bar.
    """
    global _currentBar
    if _currentBar:
        raise IllegalNestingError("can't nest progress bars")

    progress = ProgressBar()
    if size is None:
        if hasattr(seq, '__len__'):
            progress.start(len(seq))
        elif force:
            seq = list(seq)
            progress.start(len(seq))
        else:
            raise ValueError, "seq has no __len__ method"
    else:
        progress.start(size)

    _currentBar = progress

    count = 0
    for item in seq:
        yield item
        count += 1
        if count % modValue == 0:
            progress.update(count)

    progress.finish()

    _currentBar = None
    return

#----------------------------------------------------------------------------#

def tick():
    """
    Indicate activity in the current progress bar.
    """
    global _currentBar

    if _currentBar is not None:
        _currentBar.tick()
    return

#----------------------------------------------------------------------------#

class ProgressBar:
    "A progress bar which gets printed to stdout."
    def __init__(self, stringSize=20):
        "Creates a new instance, setting the size as needed."
        self._stringSize = stringSize
        self._count = 0
        self._totalCount = None
        self._lastLineSize = None
        self._lastRotation = 0
        self._startTime = None

        self._rotation = ['/', '-', '\\', '|']
        self._numRotations = len(self._rotation)

        return

    def reset(self):
        "Resets the progress bar to initial conditions."
        self._count = 0
        self._totalCount = None
        self._lastLineSize = None
        self._lastRotation = 0
        self._startTime = None

        return
    
    def start(self, totalCount):
        """
        Starts the progress bar. This will be the first output from the
        bar. At this stage it needs the total count so that it can
        calculate percentages.

        @param totalCount: The count which represents 'finished'.
        """
        assert self._count == 0, "Progress bar already started, call reset()"
        assert totalCount > 0, "Progress bar needs a non-zero total count"
        self._totalCount = totalCount
        progressLine = '[' + shellColor.color('/', 'red') + \
                (self._stringSize-1)*' ' + ']   0%'
        sys.stdout.write(progressLine)
        sys.stdout.flush()
        self._lastLineSize = shellColor.realLen(progressLine)

        self._startTime = time.time()

        return

    def update(self, count):
        """
        Updates the progress bar with the current count. This is useful
        to call even if the count has not increased, since it provides
        visual feedback to the user that the process is active.

        @param count: The current count
        """
        count = int(count)
        self._count = count
        if count < 0 or count > self._totalCount:
            raise Exception, 'Bad count for progress bar'

        n = (count * self._stringSize) / self._totalCount
        percent = (100*count) / self._totalCount
        m = self._stringSize - n - 1 # subtract one for the rotating char

        self._lastRotation = (self._lastRotation + 1) % self._numRotations
        if percent < 100:
            rotChar = self._rotation[self._lastRotation]
        else:
            rotChar = ''

        progressLine = '[' + shellColor.color(n*'-' + rotChar, 'red') + \
                m*' ' + '] ' + str('%3d%%' % percent)
        sys.stdout.write('\b'*(self._lastLineSize))
        sys.stdout.write(progressLine)
        sys.stdout.flush()
        self._lastLineSize = shellColor.realLen(progressLine)

        return

    def tick(self):
        "Perform a quick update."
        self.update(self._count)
        return

    def fractional(self, fraction):
        "Set a fractional percentage completion, e.g. 0.3333 -> 33%."
        assert fraction >= 0 and fraction <= 1
        self.update(int(fraction * self._totalCount))

        return
    
    def finish(self):
        "Fixes to 100% complete, and writes the time taken."
        assert self._totalCount > 0, "Progress bar wasn't initialised"
        self.update(self._totalCount)

        timeTaken = int(time.time() - self._startTime)
        (mins, secs) = divmod(timeTaken, 60)
        if not mins:
            timeString = ' (%ds)\n' % secs
        else:
            (hours, mins) = divmod(mins, 60)
            if not hours:
                timeString = ' (%dm %ds)\n' % (mins, secs)
            else:
                timeString = ' (%dh %dm %ds)\n' % (hours, mins, secs)

        sys.stdout.write(timeString)

        # precautionary, in case finish() is called more than once
        self._lastLineSize += len(timeString)

        return

#----------------------------------------------------------------------------#

if __name__ == '__main__':
    for i in withProgress(range(100)):
        time.sleep(0.1)
