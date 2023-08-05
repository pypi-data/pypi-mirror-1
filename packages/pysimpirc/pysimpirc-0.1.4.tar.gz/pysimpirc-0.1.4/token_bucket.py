#!/usr/bin/env python
"""Module token_bucket -- defines a simple token bucket buffer.

See class TokenBucketBuffer's documentation for extensive information.
"""

__docformat__ = "reStructuredText"

__all__ = ["TokenBucketBuffer"]

import time

class TokenBucketBuffer(object):
    """Token bucket buffering class.

    The idea behind this is from the Linux queue discipline ``TBF'' which is
    short for ``token bucket filter.'' It works by a simple method, a token
    pool (in this case it's just a counter) is regenerated over time, and
    each token may be whatever you define it as. The reason as to why it
    uses a pool instead of simply checking if enough time has passed is that
    it allows for ``bursts'' of tokens to be used.

    Example of usage:
    >>> from time import sleep
    >>> tbb = TokenBucketBuffer(max_size=100, regen_amount=10)
    >>> print tbb.free_tokens  # Starts at max_size.
    100.0
    >>> x = [tbb.append(x) for x in xrange(100)]  # Exhaust pool.
    >>> print round(tbb.free_tokens)
    0.0

    >>> # In 0.5 seconds, half the regeneration amount (10) should have been
    >>> # regenerated. (The default regeneration interval is 1 sec.)
    >>> # Note that the sleep is for 0.51 seconds to avoid the floating
    >>> # point inprecision.
    >>> sleep(0.51)
    >>> tbb.tick()  # All compensation happens here.
    >>> print round(tbb.free_tokens)
    5.0

    >>> # Appending more tokens than there are free tokens places said
    >>> # values on a buffer, each value is emitted once there are
    >>> # tokens available.
    >>> x = [tbb.append(x) for x in xrange(10)]
    >>> print int(tbb.free_tokens)
    0
    >>> print len(tbb.buffer)
    5
    
    >>> # If you have values on said buffer, wait a while and tick again,
    >>> # said values on said buffer will automatically be shifted over
    >>> # to your data buffer.
    >>> sleep(1)  # More than enough.
    >>> tbb.tick()
    >>> print len(tbb.buffer)
    0

    >>> # It is also possible to specify a callback, either in the
    >>> # constructor or setting it yourself, which will be
    >>> # called *instead* of adding to the object's data buffer.
    >>> def printer(value):
    ...     print "do something with", value
    ... 
    >>> tbb.callback = printer  # The current data buffer is left intact.
    >>> tbb.append("foo string")
    do something with foo string
    >>> bool(tbb.data)  # There's still data.
    True
    """

    def __init__(self, max_size=4, regen_interval=1, regen_amount=1, callback=None):
        """Initialize a token bucket bufferer.

        ``max_size'' is the maximal size of the bucket.
        ``regen_interval'' is the interval of seconds that it should take to
        regenerate ``regen_amount'' of tokens.
        If ``callback'' is specified (evaluates to True), it is called
        instead of adding to ``self.data''.
        """

        self.free_tokens = float(max_size)
        self.max_size = max_size
        self.data = []
        self.buffer = []
        self.regen_interval = regen_interval
        self.regen_amount = regen_amount
        self.last_tick = time.time()
        self.callback = callback

    def _shove(self, value):
        """Shoves given value out to either data buffer or to callback."""

        if self.callback:
            self.callback(value)
        else:
            self.data.append(value)


    def append(self, value):
        """Append value to either output buffer or shove it out."""

        if self.free_tokens < 1:
            self.buffer.append(value)
        else:
            self.free_tokens -= 1
            self._shove(value)

    def tick(self):
        """Increments free token count and shoves out buffered values.

        Compensates for time passed between last tick and current tick.
        """

        current_time = time.time()
        passed_time = float(current_time - self.last_tick)
        # new_tokens = passed_time / regen_interval * regen_amount
        self.free_tokens += passed_time / self.regen_interval * self.regen_amount
        self.free_tokens = min(self.max_size, self.free_tokens)
        self.last_tick = current_time
        while self.buffer and self.free_tokens > 1:
            # self.buffer is a stack (LIFO)
            self._shove(self.buffer.pop(0))
            self.free_tokens -= 1

def _test():
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    _test()
