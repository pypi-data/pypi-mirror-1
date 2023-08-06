"""Provides a common component interface.

Filters should subclass this module and impliment 
the run() method.

"""

import stackless

class Component(object):
    """Provides methods common to all filters.

    Anyone building a custom filter object should
    subclass this module and implement their own
    run() method.

    Keep in mind that filters are stackless.tasklets
    and the run method should yield rather return.

    @status: Stable
    @since: Nov. 25 2008
    @author: U{Eric Gaumer<mailto:egaumer@mac.com>}
    @todo: none

    """
    __metatype__ = None 
    def __init__(self):
        """Class constructor

        Provides default input of 'in' and output of 'out'.
        """
        self.inputs  = {'in' : [None, 'Default input port'] }
        self.outputs = {'out': [None, 'Default output port']}
        self._parameters = {}

    def run(self):
        """Starts this component as a stackless tasklet

        This method is meant to be overridden in derived subclass.
        The subclass should implement its own logic.

        @status: Stable
        @since: Nov. 25 2008
        @author: U{Eric Gaumer<mailto:egaumer@mac.com>}
        @todo: none

        """
        raise NotImplementedError

    def Yield(self):
        """Causes this tasklet to relinquish control of the 
        CPU to allow another tasklet to run. This tasklet is
        re-scheduled to run again.

        @return: Nothing
        @status: Stable
        @since: Nov. 25, 2008
        @author: U{Eric Gaumer<mailto:egaumer@mac.com>}
        @todo: Nothing
        """
        stackless.schedule()

    def addInput(self, name, desc=None):
        """Adds a new input port to this component.

        This is most typically called from the object
        subclassing this component. Adding a new port means 
        you are adding some filter logic that utilizes 
        the new port in some way.

        @param name: The string used to represent this port
        @type name: String
        
        @keyword desc: An optional description of what this port is used for.
        @note: Although desc is optional, it is considered good practice 
               to provide a brief description.

        @return: Nothing
        @status: Stable
        @since: Nov. 25, 2008
        @author: U{Eric Gaumer<mailto:egaumer@mac.com>}
        @todo: Nothing
        """
        status = False
        if not self.inputs.has_key(name):
            self.inputs[name] = [None, desc]
            status = True
        return status
    
    def removeInput(self, name):
        """Removes the given port from this components list of available input ports.

        @param name: The string used to represent this port
        @type name: String

        @return: Nothing
        @status: Stable
        @since: Dec. 09, 2008
        @author: U{Eric Gaumer<mailto:egaumer@mac.com>}
        @todo: Nothing
        """
        status = False
        if self.inputs.has_key(name):
            self.inputs.pop(name)
            status = True
        return status

    def addOutput(self, name, desc=None):
        """Adds a new output port to this component.

        This is most typically called from the object
        subclassing this component. Adding a new port means 
        you are adding some filter logic that utilizes 
        the new port in some way.

        @param name: The string used to represent this port
        @type name: String
        
        @keyword desc: An optional description of what this port is used for.
        @note: Although desc is optional, it is considered good practice 
               to provide a brief description.

        @return: Nothing
        @status: Stable
        @since: Nov. 25, 2008
        @author: U{Eric Gaumer<mailto:egaumer@mac.com>}
        @todo: Nothing
        """
        status = False
        if not self.outputs.has_key(name):
            self.outputs[name] = [None, desc]
            status = True
        return status
    
    def removeOutput(self, name):
        """Removes the given port from this components list of available output ports.

        @param name: The string used to represent this port
        @type name: String

        @return: Nothing
        @status: Stable
        @since: Dec. 09, 2008
        @author: U{Eric Gaumer<mailto:egaumer@mac.com>}
        @todo: Nothing
        """
        status = False
        if self.outputs.has_key(name):
            self.outputs.pop(name)
            status = True
        return status

    def connectInput(self, name, edge):
        """Connects a edge (pype) to the specified input port of this component.

        This only represents half of an actual connection between two nodes.
        Typically, one side of the edge is connected to the output of one
        node while the other side is connected to the input of another node.

        @see: L{connectOutput}

        @param name: The string used to represent this port
        @type name: String
        
        @param edge: The edge you would like to connect
        @type edge: L{Pype}

        @return: Nothing
        @status: Stable
        @since: Nov. 25, 2008
        @author: U{Eric Gaumer<mailto:egaumer@mac.com>}
        @todo: Need to raise custom excpetion when trying to connect
               a non-existant port.
        """
        try:
            item = self.inputs[name]
        except:
            print 'Input does not exist'
        else:
            item[0] = edge
            self.inputs[name] = item

    def connectOutput(self, name, edge):
        """Connects a edge (pype) to the specified output port of this component.

        This only represents half of an actual connection between two nodes.
        Typically, one side of the edge is connected to the output of one
        node while the other side is connected to the input of another node.

        @see: L{connectInput}

        @param name: The string used to represent this port
        @type name: String
        
        @param edge: The edge you would like to connect
        @type edge: L{Pype}

        @return: Nothing
        @status: Stable
        @since: Nov. 25, 2008
        @author: U{Eric Gaumer<mailto:egaumer@mac.com>}
        @todo: Need to raise custom exception when trying to connect
               a non-existant port.
        """
        try:
            item = self.outputs[name]
        except:
            print 'Output does not exist'
        else:
            item[0] = edge
            self.outputs[name] = item

    def isConnected(self, name):
        """Returns True is the specified port is connected to an edge.

        @param name: The port being referenced
        @type name: String
        @return: Boolean
        @status: Stable
        @since: Nov. 25, 2008
        @author: U{Eric Gaumer<mailto:egaumer@mac.com>}
        @todo: Nothing
        """
        status = False
        in_connected = False
        out_connected = False

        if self.inputs.has_key(name):
            in_connected = self.inputs[name][0]

        if self.outputs.has_key(name):
            out_connected = self.outputs[name][0]

        connected = in_connected or out_connected

        if connected:
            status = True

        return status

    def getPortDesc(self, port):
        """Returns the ports description.

        @param port: The port being referenced
        @type port: String
        @return: String
        @status: Stable
        @since: Nov. 25, 2008
        @author: U{Eric Gaumer<mailto:egaumer@mac.com>}
        @todo: Need to raise custom exception when trying to query
               a non-existant port.
        """
        desc = None

        if self.hasPort(port):
            try:
                desc = self.inputs[port][1]
            except:
                desc = self.outputs[port][1]

        return desc

    def setPortDesc(self, port, desc):
        """Sets the ports description.

        @param port: The port being referenced
        @type port: String
        @return: Nothing
        @status: Stable
        @since: Nov. 25, 2008
        @author: U{Eric Gaumer<mailto:egaumer@mac.com>}
        @todo: Need to raise custom exception when trying to query
               a non-existant port.
        """
        if self.hasPort(port):
            try:
                item = self.inputs[port]
                item[1] = desc
                self.inputs[port] = item
            except:
                item = self.outputs[port]
                item[1] = desc
                self.outputs[port] = item
            

    def hasPort(self, port):
        """Returns True if the component contains this port, False otherwise.

        @param port: The port being referenced
        @type port: String
        @return: Boolean
        @status: Stable
        @since: Nov. 25, 2008
        @author: U{Eric Gaumer<mailto:egaumer@mac.com>}
        @todo: Nothing
        """
        return self.inputs.has_key(port) or self.outputs.has_key(port)

    def recv(self, port):
        """Tries recieving data on the specified port.

        @param port: The port being referenced
        @type port: String
        @return: Incoming data or None if no data is available
        @status: Stable
        @since: Nov. 25, 2008
        @author: U{Eric Gaumer<mailto:egaumer@mac.com>}
        @todo: Nothing
        """
        try:
            data = self.inputs[port][0].recv()
        except:
            data = None
        return data
    
    def send(self, port, data):
        """Sends data on specified port.

        @param port: The port being referenced
        @type port: String

        @param data: Data to be sent
        @type data: Application specific

        @return: Boolean (depending on the success)
        @status: Stable
        @since: Nov. 25, 2008
        @author: U{Eric Gaumer<mailto:egaumer@mac.com>}
        @todo: Nothing
        """
        status = True
        try:
            self.outputs[port][0].send(data)
        except:
            status = False
        return status

    def getInPorts(self):
        """Returns a list of current inputs ports for this component.

        @status: Stable
        @since: Nov. 25, 2008
        @author: U{Eric Gaumer<mailto:egaumer@mac.com>}
        @todo: Nothing
        """
        return self.inputs.keys()

    def getOutPorts(self):
        """Returns a list of current output ports for this component.

        @status: Stable
        @since: Nov. 25, 2008
        @author: U{Eric Gaumer<mailto:egaumer@mac.com>}
        @todo: Nothing
        """
        return self.outputs.keys()

    def getParameters(self):
        """Returns a dict of parameters used by this component.

        @return: dict
        @status: Stable
        @since: Jun. 03, 2009
        @author: U{Eric Gaumer<mailto:egaumer@mac.com>}
        @todo: Nothing
        """
        return self._parameters

    def setParameters(self, parameters):
        """Sets parameters for this component.

        @param parameters: The parameters being set on this component
        @type parameters: dict
        @status: Stable
        @since: Jun. 03, 2009
        @author: U{Eric Gaumer<mailto:egaumer@mac.com>}
        @todo: Nothing
        """
        self._paramaters = parameters

    def getParam(self, name):
        """Returns a specific parameter for this component.

        @param name: The name of the parameter you want
        @type name: String
        @return: String
        @status: Stable
        @since: Jun. 03, 2009
        @author: U{Eric Gaumer<mailto:egaumer@mac.com>}
        @todo: Nothing
        """
        try:
            p = self._parameters[name][0]
        except:
            p = None
        return p

    def setParam(self, name, parameter, options=None):
        """Sets a specific parameter for this component.

        @param name: The name of teh parameter being set
        @type name: String
        @param parameter: The value being set for this parameter
        @type parameter: String
        @status: Stable
        @since: Nov. 25, 2008
        @author: U{Eric Gaumer<mailto:egaumer@mac.com>}
        @todo: Nothing
        """
        if options is None and self._parameters.has_key(name):
            pset = self._parameters[name][0] = parameter
        else:
            if options is None or not isinstance(options, list):
                options = []
            try:
                self._parameters[name] = [parameter, options]
            except:
                pass

    def getType(self):
        return self.__metatype__

    # properties 
    Inputs = property(getInPorts)   
    Outputs = property(getOutPorts)
    parameters = property(getParameters, setParameters)
    type = property(getType)

