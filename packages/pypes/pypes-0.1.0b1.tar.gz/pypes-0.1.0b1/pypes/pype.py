"""Provides the buffer that connects two filters.

This class serves as the edges of the graph. Nodes
attached to either end send and recieve data through
a pype instance.

Each pair of nodes is connected by their own unique
pype object.
"""

class Pype(object):
    """A bidirectional buffer used to allow two nodes to pass data back and forth.

    @status: Stable
    @since: Nov. 25 2008
    @author: U{Eric Gaumer<mailto:egaumer@mac.com>}
    @todo: Should this be a L{multiprocessor.pipe}?
    """
    def __init__(self):
        """Class constructor
        """
        self.buffer = []

    def getBufferSize(self):
        """Returns the current buffer size of this pype

        @note: filters don't typically buffer data
               so (for now) this return value should
               almost always be 0 or 1.
        @status: Stable
        @since: Nov. 25, 2008
        @author: U{Eric Gaumer<mailto:egaumer@mac.com>}
        @todo: Nothing
        """
        return len(self.buffer)

    size = property(getBufferSize)

    def send(self, data):
        """Writes data to this pype

        @return: Nothing
        @status: Stable
        @since: Nov. 25, 2008
        @author: U{Eric Gaumer<mailto:egaumer@mac.com>}
        @todo: Nothing
        """
        self.buffer.append(data)

    def recv(self):
        """Reads data from this pype

        @return: data or None if no data is available
        @status: Stable
        @since: Nov. 25, 2008
        @author: U{Eric Gaumer<mailto:egaumer@mac.com>}
        @todo: Nothing
        """
        try:
            data = self.buffer.pop(0)
        except:
            data = None
        return data

