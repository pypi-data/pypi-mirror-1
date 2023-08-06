"""Provides scheduling routines for stackless tasklets.

The scheduler itself runs as a tasklet. It blocks waiting
for input on the channel passed in. When new data is sent
on this channel, the scheduler wakes and begins processing
of the data.

"""

import stackless
from pype import Pype
from graph import get_pairlist, topsort
import sys
import traceback

def sched(ch, graph):
    """Sits in an infinite loop waiting on the channel to recieve data.

    The procedure prolog takes care of sorting the
    input graph into a dependency list and initializing
    the filter tasklets used to construct the graph.

    @param graph: The graph representing the work flow
    @type graph: Python dict organized as a graph struct
    @param ch: The stackless channel to listen on
    @type ch: stackless.channel
    @return: nothing
    @status: stable
    @since: Nov. 25 2008
    @author: Eric Gaumer
    @todo: none  
    """
    edgeList = get_pairlist(graph)
    nodes = topsort(edgeList)
    tasks = []
    inputEdge = Pype()
    
    for n in nodes:
        # start this microthread
        tasks.append(stackless.tasklet(n.run)())
        try:
            # get this nodes outputs
            edges = graph[n]
        except:
            pass
        else:
            # for each output
            for e in edges:
                e1 = Pype()
                # does this port exist
                if not n.hasPort(edges[e][0]):
                    print 'Trying to connect undefined output port', n, edges[e][0]
                    sys.exit(1)

                n.connectOutput(edges[e][0], e1)
                    
                # does this port exist 
                if not e.hasPort(edges[e][1]):
                    print 'Trying to connect undefined input port', e, edges[e][1]
                    sys.exit(1)

                e.connectInput(edges[e][1], e1)

    # Added so that incoming data is fed to every input adapter
    # should check if in exists and create it if it doesn't 
    # because a user could remove the input port by accident
    inputEdges = []
    for n in nodes:
        if n.type == 'ADAPTER':
            ie = Pype()
            n.connectInput('in', ie)
            inputEdges.append(ie)
    #nodes[0].connectInput('in', inputEdge)

    while True:
        data = ch.receive()
        for ie in inputEdges:
            ie.send(data)
        #inputEdge.send(data)
        try:
            tasks[0].run()
        except:
            traceback.print_exc()

