'''Dispatches chunks of frames to be rendered by nodes.'''

import os.path
import threading
import glob

import multiblend.logging
log = multiblend.logging.Logger(__name__)


class FrameDispatcher(object):
    '''Frame dispatcher for render nodes.

    The dispatcher is initialized with a starting and ending frame
    number, and the size of the chunks dispatched. Every rendering
    thread can then ask for a new chunk of frames to render. When no
    more frames are available, None is returned.

    This dispatching is done in a thread-safe fashion. Threads can
    thus simply call chunk() without having to mess with locks etc.

    >>> fd = FrameDispatcher(1, 201, 100, 1)
    >>> fd.chunk()
    (1, 100)
    >>> fd.chunk()
    (101, 200)
    >>> fd.chunk()
    (201, 201)
    >>> fd.chunk()

    The frames will be evenly distributed among nodes:

    >>> fd = FrameDispatcher(1, 101, 100, 3)
    >>> fd.chunk()
    (1, 34)
    >>> fd.chunk()
    (35, 68)
    >>> fd.chunk()
    (69, 101)
    '''

    def __init__(self, start, end, chunksize, node_count, output_path=None):
        '''Constructor, see class docstring for usage.'''
        
        self.start = start
        self.end = end

        if chunksize < 1:
            raise ValueError('Chunk size should be > 0')
        if start > end:
            raise ValueError('Start should be before end')

        # Figure out the chunks we have to render
        if output_path:
            ranges = self._find_ranges(start, end, output_path)
        else:
            ranges = [(start, end)]
        self.chunks = self._split_ranges(ranges, chunksize, node_count)

        log.debug('Created new %s %i -> %i, %i-size chunks' %
                (self.__class__, start, end, chunksize))
        log.debug('Chunks: %s' % self.chunks)

        self.lock = threading.RLock()

    def __str__(self):
        return '[%s %i -> %i, %i-size chunks]' % \
                (self.__class__, self.start, self.end, self.chunksize)

    def __unicode__(self):
        return unicode(str(self))

    def _find_ranges(self, start, end, output_path):
        '''Returns a list of ranges [(r_start, r_end), ...] of non-existing
        frames in the output path.
        '''

        log.info('Finding missing frames on %s' % output_path)

        def framenr(filename):
            basename = os.path.basename(filename)
            (frame, ext) = os.path.splitext(basename)
            try:
                return int(frame, 10)
            except ValueError:
                return None

        # Start by getting a list of rendered frames.
        files = glob.glob(os.path.join(output_path, '[0-9]*'))
        rendered = set()
        for f in files:
            nr = framenr(f)
            if nr is not None: rendered.add(nr)
        #log.debug('Rendered frames: %s' % rendered)

        # Examine the frame numbers to find holes.
        allframes = set(range(start, end+1))
        missing = sorted(list(allframes - rendered))
        #log.debug('Missing frames: %s' % missing)

        # Now group the missing frames into ranges
        ranges = []
        start = None
        total_missing = len(missing)
        for index, thisframe in enumerate(missing):
            # This frame is the start if we're not in a range already
            if start is None:
                start = thisframe
            
            # This frame is the end if this is the last frame, or the next frame
            # is more than one frame away
            if index == total_missing - 1 or missing[index+1] > thisframe+1:
                end = thisframe
                ranges.append((start, end))

                # Start over with a new range
                start = None

        log.info('Missing frames: %s' % ', '.join(['%s-%s' % r for r in ranges]))
        return ranges

    def _split_ranges(self, ranges, chunksize, node_count):
        '''Splits the ranges into chunks, obeying the maximum chunk size
        'chunksize', but also maximizing the distribution over the different
        nodes.
        '''

        nr_of_frames = sum(end - start + 1 for (start, end) in ranges)
        chunksize = min(chunksize, nr_of_frames / node_count + 1)

        chunks = []
        ranges = ranges[:] # get a local copy of the list
        while ranges:
            start, end = ranges.pop(0)
        
            # If the range is larger than the maximum chunk size, we can't use
            # the entire range and have to split it up
            if end - start + 1 > chunksize:
                new_start = start + chunksize

                # Put a new range back
                ranges.insert(0, (new_start, end))
                end = new_start - 1
            
            chunks.append((start, end))
        
        return chunks

    def chunk(self):
        '''Returns a new chunk of frames.

        Returns a tuple (start, end) or None if there are no more
        frames to dispatch.
        '''

        self.lock.acquire()
        if self.chunks:
            range = self.chunks.pop(0)
        else:
            # We're out of frames to render.
            range = None
        self.lock.release()

        log.debug('Chunks left: %s' % self.chunks)

        return range

    def reset(self):
        '''Resets the FrameDispatcher.

        Subsequent calls to chunk() will return the same values as
        when the FrameDispatcher was just created.
        '''

        self.lock.acquire()
        self.next_chunk = self.start
        self.lock.release()
