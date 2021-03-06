from mesh.generic.nodeState import LinkStatus

class NodeController(object):   
    """Generic node controller to subtype for specific vehicle types.

    Attributes:
        logFile: File object for logging node data.
        logTime: Time of last write to log file.
        nodeConfig: NodeConfig instance that stores configuration data for this node.
    """

    def __init__(self, nodeParams, logFile=[]):
        # Logging
        self.logFile = logFile      
        self.logTime = 0
    
        # Node configuration
        self.nodeParams = nodeParams
    
    def controlNode(self):
        """Function that controls node logic execution.  This functions calls the other node
        logic in the proper order for node execution."""

        # Process commmands
        self.processCommands()

        # Check status of other formation nodes
        self.monitorFormationStatus()
        
        # Run unique node behavior
        self.executeNode()  

        # Log data
        self.logData()

    def executeNode(self):
        """Executes primary formation node processing logic that determines where this node
        should be in the particular formation and how to get it into the desired state."""
        pass        

    def processFCCommands(self, FCComm):
        """Performs initial processing of incoming commands and messages from the vehicle's flight computer."""
        pass

    def processNodeCommands(self, comm):
        """Performs initial processing of incoming commands and messages from formation mesh network."""
        pass

    def processCommands(self):
        """Performs more specific processing and implementation of commands received over the 
        formation mesh network."""
        pass

    def logData(self):
        """Logs pertinent node operational and state data."""
        pass

    def monitorNodeUpdates(self):
        """Monitors times since last state update from other nodes."""
        
        # Check that other nodes' states are updating
        if 'nodeStatus' not in self.nodeParams.__dict__ or 'clock' not in self.nodeParams.__dict__:
            return
        for node in self.nodeParams.nodeStatus:
            if (node.lastStateUpdateTime + self.nodeParams.config.nodeUpdateTimeout) < self.nodeParams.clock.getTime(): 
                node.updating = False
            else:
                node.updating = True 
        
    def checkNodeLinks(self):
        """Checks status of links to other nodes."""
        thisNode = self.nodeParams.config.nodeId - 1
        for i in range(self.nodeParams.config.maxNumNodes):
            if (i == thisNode): # this node
                self.nodeParams.linkStatus[thisNode][i] = LinkStatus.GoodLink
            else: # other nodes
                # Check for direct link
                if (self.nodeParams.nodeStatus[i].present and (self.nodeParams.clock.getTime() - self.nodeParams.nodeStatus[i].lastMsgRcvdTime) < 1.5*self.nodeParams.config.commConfig['frameLength']):
                    #if ((self.nodeParams.clock.getTime() - self.nodeParams.nodeStatus[i].lastMsgRcvdTime) < 1.5*self.nodeParams.config.commConfig['frameLength']):
                    self.nodeParams.linkStatus[thisNode][i] = LinkStatus.GoodLink
                
                # Check for indirect link
                elif (self.nodeParams.nodeStatus[i].updating == True): # state data is updating, so at least an indirect link
                    self.nodeParams.linkStatus[thisNode][i] = LinkStatus.IndirectLink
                
                else: # no link
                    if (self.nodeParams.linkStatus[thisNode][i] != LinkStatus.NoLink): # lost link
                        self.nodeParams.linkStatus[thisNode][i] = LinkStatus.BadLink
                #else: # no link ever with this node
                #    self.nodeParams.linkStatus[thisNode][i] = LinkStatus.NoLink

    def monitorFormationStatus(self):
        """Monitors status of other formation nodes to determine their current status."""

        # Check update status
        self.monitorNodeUpdates()

        # Check node links
        self.checkNodeLinks()
