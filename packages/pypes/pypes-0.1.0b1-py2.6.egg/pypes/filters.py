"""Provides various basic filters that mimic Unix filters
such as grep, cut, sort, uniq, etc...

Most of these basic filters operate on strings or lines
of strings just as you would expect from the Unix versions.
"""

import stackless
from component import Component

class Null(Component):
    __metatype__ = 'FILTER'
    """A Null filter used to silently swallow data similar to /dev/null
    
    @status: Stable
    @since: Nov. 25 2008
    @author: U{Eric Gaumer<mailto:egaumer@mac.com>}
    @todo: none
    """
    def __init__(self):
        """Class constructor 
        """
        Component.__init__(self)

    def run(self):
        """Entry point for this component. Overrides L{Component.run}
        """
        while True:
            data = self.recv('in')
            self.Yield()
"""
class Reverse(Component):
    def __init__(self):
        Component.__init__(self)

    def run(self):
        while True:
            data = self.recv('in')
            chars = [c for c in data]
            chars.reverse()
            d = ''.join(chars)
            self.send('out', d)
            self.Yield()

"""

class TextFileInputReader(Component):
    __metatype__ = 'ADAPTER'
    """Filter used to consume ASCII text files

    @status: Stable
    @since: Nov. 25 2008
    @author: U{Eric Gaumer<mailto:egaumer@mac.com>}
    @todo: none
    """
    def __init__(self):
        """Class constructor 
        """
        Component.__init__(self)
        #self.removeInput('in')

    def run(self):
        """Entry point for this component. Overrides L{Component.run}
        """
        while True:
            data = self.recv('in')
            fp = open(data, 'rb')
            lines = fp.readlines()
            fp.close()
            self.send('out', lines)
            self.Yield()

class StringInputReader(Component):
    __metatype__ = 'ADAPTER'
    """Filter used to consume strings

    @status: Stable
    @since: Nov. 25 2008
    @author: U{Eric Gaumer<mailto:egaumer@mac.com>}
    @todo: none
    """
    def __init__(self):
        """Class constructor 
        """
        Component.__init__(self)
        #self.removeInput('in')

    def run(self):
        """Entry point for this component. Overrides L{Component.run}
        """
        while True:
            data = self.recv('in')
            self.send('out', [data])
            self.Yield()

class ConsoleOutputWriter(Component):
    """Filter that emulates Unix stdout

    @status: Stable
    @since: Nov. 25 2008
    @author: U{Eric Gaumer<mailto:egaumer@mac.com>}
    @todo: none
    """
    def __init__(self):
        """Class constructor 
        """
        Component.__init__(self)
        self.removeOutput('out')

    def run(self):
        """Entry point for this component. Overrides L{Component.run}
        """
        while True:
            data = self.recv('in')
            for line in data:
                line = line.strip()
                print line
            
            self.Yield()

class Grep(Component):
    """Filter that emulates the Unix grep command

    @status: Stable
    @since: Nov. 25 2008
    @author: U{Eric Gaumer<mailto:egaumer@mac.com>}
    @todo: none
    """
    def __init__(self, expression):
        """Class constructor 

        @param expression: the expression we want to grep
        @type expression: String
        @status: Stable
        @since: Nov. 25 2008
        @author: U{Eric Gaumer<mailto:egaumer@mac.com>}
        @todo: Should handle regular expressions
        """
        Component.__init__(self)
        self.expression = expression

    def run(self):
        """Entry point for this component. Overrides L{Component.run}
        """
        while True:
            data = self.recv('in')
            items = []

            for line in data:
                if self.expression in line:
                    items.append(line)

            self.send('out', items)
            self.Yield()

class Sort(Component):
    """Filter that emulates the Unix sort command

    @status: Stable
    @since: Nov. 25 2008
    @author: U{Eric Gaumer<mailto:egaumer@mac.com>}
    @todo: none
    """
    def __init__(self, direction='ascending'):
        """Class constructor

        @keyword direction: ascending|descending sort order
        @type direction: String
        @status: Stable
        @since: Nov. 25 2008
        @author: U{Eric Gaumer<mailto:egaumer@mac.com>}
        @todo: Nothing
        """
        Component.__init__(self)

        if direction not in ['ascending', 'descending']:
            direction = 'ascending'

        if direction == 'ascending':
            self.direction = False
        else:
            self.direction = True

    def run(self):
        """Entry point for this component. Overrides L{Component.run}
        """
        while True:
            data = self.recv('in')
            data.sort(reverse=self.direction)
            self.send('out', data)
            self.Yield()

class BinarySplit(Component):
    """Filter that forks data into two output paths

    @status: Stable
    @since: Nov. 25 2008
    @author: U{Eric Gaumer<mailto:egaumer@mac.com>}
    @todo: Rename to fork?
    """
    def __init__(self):
        """Class constructor 
        """
        Component.__init__(self)
        self.addOutput('out2', 'duplicates output on this port')

    def run(self):
        """Entry point for this component. Overrides L{Component.run}
        """
        while True:
            data = self.recv('in')
            self.send('out', data)
            self.send('out2', data)
            self.Yield()

class Uniq(Component):
    """Filter that emulates the Unix uniq command

    @status: Stable
    @since: Nov. 25 2008
    @author: U{Eric Gaumer<mailto:egaumer@mac.com>}
    @todo: none
    """
    def __init__(self):
        """Class constructor 
        """
        Component.__init__(self)

    def run(self):
        """Entry point for this component. Overrides L{Component.run}
        """
        while True:
            data = self.recv('in')
            uniq = {}
            count = 0

            for line in data:
                uniq[count] = line
                count += 1

            keys = [uniq[i] for i in range(len(uniq))]

            self.send('out', keys)
            self.Yield()

class Cut(Component):
    """Filter that emulates the Unix cut command

    @status: Stable
    @since: Nov. 25 2008
    @author: U{Eric Gaumer<mailto:egaumer@mac.com>}
    @todo: none
    """
    def __init__(self, *fields, **kwargs):
        """Class constructor

        @param fields: the field numbers to be cut
        @param fields: int
        @keyword sep: default separator to use (defaults to 0x20)
        @type sep: String
        @status: Stable
        @since: Nov. 25 2008
        @author: U{Eric Gaumer<mailto:egaumer@mac.com>}
        @todo: Nothing
        """
        Component.__init__(self)
        self.indicies = fields
        try:
            self.sep = kwargs['sep']
        except:
            self.sep = ' '

    def run(self):
        """Entry point for this component. Overrides L{Component.run}
        """
        while True:
            data = self.recv('in')

            doc = []
            for line in data:
                tokens = []
                parts = line.split(self.sep)

                for i in self.indicies:
                    try:
                        tokens.append(parts[i-1])
                    except:
                        pass
                this_string = ' '.join(tokens)
                doc.append(this_string)

            self.send('out', doc)
            self.Yield()

