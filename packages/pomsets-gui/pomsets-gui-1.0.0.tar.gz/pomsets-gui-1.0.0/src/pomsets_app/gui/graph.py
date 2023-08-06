import logging
import os

import pypatterns.filter as FilterModule
import pypatterns.relational as RelationalModule
import pomsets.resource as ResourceModule

import pomsets.definition as DefinitionModule
import pomsets.task as TaskModule
import pomsets.parameter as ParameterModule

import zgl_graphdrawer.Edge as EdgeModule
import zgl_graphdrawer.Node as NodeModule
import zgl_graphdrawer.Port as PortModule
import zgl_graphdrawer.VisualPolicy as VisualPolicyModule

import zgl.zglPrimitives as PrimitivesModule
import zgl.zglText as TextModule

from PyQt4.QtCore import *

IMAGE_SELECTED_TRUE = 'image selected'
IMAGE_SELECTED_FALSE = 'image not selected'
IMAGE_PARAMETER_SWEEP = 'image parameter sweep'


class Node(NodeModule.Node, ResourceModule.Struct):

    WIDTH = 100
    HEIGHT = 50

    ATTRIBUTES = [
        'task',
        'statusUpdater',
        'executionStatusPerformer',
        'childTasksPerformer',
        'shouldDisplayExecutionStatus'
    ]

    PART_EXECUTE_STATUS = 'execute status'
    PART_DISPLAY_IMAGES = 'display images'

    @staticmethod
    def hasCustomDragReleaseCallback():
        return True

    
    @staticmethod
    def OnDrag(*args, **kwds):
        retVal = NodeModule.Node.OnDrag(*args, **kwds)        
        
        # we can now go through the objects
        # retrieve their new positions
        # (already calculated for us by NodeModule.Node.OnDrag)
        # and set that on the GUI
        for object in kwds.get('objects', []):
            if not isinstance(object, Node):
                continue
            dataNode = object.nodeData
            guiOptions = dataNode.guiOptions()
            guiOptions['canvas position'] = object.getPosition()
            pass
            
        return
    
    
    def __init__(self, nodeData, *args, **kwds):
        NodeModule.Node.__init__(self, nodeData, *args, **kwds)
        ResourceModule.Struct.__init__(self)

        return

    def _buildChildren(self):
        """
        returns the parts that are to be drawn
        """

        parts = []

        imageMap = self.parts.get(Node.PART_DISPLAY_IMAGES, {})
        if IMAGE_PARAMETER_SWEEP in imageMap:
            parts.append(imageMap[IMAGE_PARAMETER_SWEEP])
        if IMAGE_SELECTED_TRUE in imageMap:
            parts.append(imageMap[IMAGE_SELECTED_TRUE])
        if IMAGE_SELECTED_FALSE in imageMap:
            parts.append(imageMap[IMAGE_SELECTED_FALSE])

        parts.extend(NodeModule.Node._buildChildren(self))

        if self.shouldDrawExecuteStatus():
            parts.append(self.parts[Node.PART_EXECUTE_STATUS])

        return parts


    def partPrimitives(self):
        return self.children()

    
    def OnDragRelease(self, event, canvas=None, 
                      objects=None,
                      eventHandler=None):

        contextManager = canvas.contextManager()
        frame = contextManager.app().GetTopWindow()

        # if the start of the drag
        # was from the library definitions (or loaded definitions)
        # then create a new node
        if hasattr(frame, 'dragSelection') and \
           frame.dragSelection is not None:

            frame.processDragSelection(event)
            pass

        eventHandler.resetMouseCallbacks()
        
        # TODO:
        # this should use the command pattern instead
        contextManager.activePomsetContext().isModified(True)
        
        # TODO:
        # need to update the active pomset ctrl
        # so that it shows that the pomset has been modified
        frame.populateActivePomsetTreeCtrl()
        
        return

    
    def configurePerformers(self, task):

        self.task(task)

        parentTask = task.parentTask()
        taskInfo = parentTask.getTaskInformation(task)
        values = taskInfo._values
        guiNode = self

        #import peak.events
        #from peak.events import trellis
        import mext.reaction.component as trellis
        # import pomsets_app.gui.event as EventModule
        
        logging.debug("in configurePerformers")
        
        class StatusUpdater(trellis.Component):
            @trellis.maintain
            def update(self):

                logging.debug("performer.update")
                
                if not hasattr(values, 'changed'):
                    return

                changes = getattr(values, 'changed')
                if not 'status' in changes:
                    return

                guiNode.updateExecuteStatus(changes['status'])
                #event = EventModule.TaskStatusChangedEvent(node=guiNode,
                #                               status=changes['status'])
                #task.automaton().contextManager().postEvent(event)
                task.automaton().contextManager().mainWindow().emit(
                    SIGNAL("OnTaskExecutionStatusChanged()"))

                        
                return
            # END class StatusUpdater
            pass

        statusUpdater = StatusUpdater()
        self.statusUpdater(statusUpdater)

        return

    def shouldDrawExecuteStatus(self):
        dataNode = self.nodeData
        guiOptions = dataNode.guiOptions()
        return guiOptions.get('should draw execute status', True)

    def shouldDrawTemporalParameters(self):
        dataNode = self.nodeData
        guiOptions = dataNode.guiOptions()
        return guiOptions.get('should draw temporal parameters', True)
        

    def retrieveInputPortNamesFromDataObject(self):
        # getParametersByFilter

        filter = FilterModule.constructAndFilter()

        filter.addFilter(
            FilterModule.ObjectKeyMatchesFilter(
                filter = FilterModule.EquivalenceFilter(ParameterModule.PORT_DIRECTION_INPUT),
                keyFunction=lambda x: x.portDirection()
            )
        )

        if not self.shouldDrawTemporalParameters():
            notTemporalFilter = FilterModule.constructNotFilter()
            notTemporalFilter.addFilter(
                FilterModule.ObjectKeyMatchesFilter(
                    filter=FilterModule.EquivalenceFilter(ParameterModule.PORT_TYPE_TEMPORAL),
                    keyFunction=lambda x: x.portType()
                )
            )
            filter.addFilter(notTemporalFilter)

        notSideEffectFilter = FilterModule.constructNotFilter()
        notSideEffectFilter.addFilter(
            FilterModule.ObjectKeyMatchesFilter(
                filter=FilterModule.IdentityFilter(True),
                keyFunction=lambda x: x.getAttribute(ParameterModule.PORT_ATTRIBUTE_ISSIDEEFFECT)
            )
        )
        filter.addFilter(notSideEffectFilter)

        parameters = self.nodeData.getParametersByFilter(filter)
        
        parameterNames = [x.id() for x in parameters]
        return parameterNames



    def retrieveOutputPortNamesFromDataObject(self):
        filter = FilterModule.constructOrFilter()

        outputValueFilter = FilterModule.ObjectKeyMatchesFilter(
            filter = FilterModule.EquivalenceFilter(ParameterModule.PORT_DIRECTION_OUTPUT),
            keyFunction=lambda x: x.portDirection()
        )

        if not self.shouldDrawTemporalParameters():
            f = FilterModule.constructAndFilter()
            f.addFilter(outputValueFilter)
            outputValueFilter = f
            
            notTemporalFilter = FilterModule.constructNotFilter()
            notTemporalFilter.addFilter(
                FilterModule.ObjectKeyMatchesFilter(
                    filter=FilterModule.EquivalenceFilter(ParameterModule.PORT_TYPE_TEMPORAL),
                    keyFunction=lambda x: x.portType()
                )
            )
            outputValueFilter.addFilter(notTemporalFilter)
            pass
        
        filter.addFilter(outputValueFilter)
        filter.addFilter(
            FilterModule.ObjectKeyMatchesFilter(
                filter=FilterModule.IdentityFilter(True),
                keyFunction=lambda x: x.getAttribute(ParameterModule.PORT_ATTRIBUTE_ISSIDEEFFECT)
            )
        )

        parameters = self.nodeData.getParametersByFilter(filter)
        parameterNames = [x.id() for x in parameters]
        return parameterNames

    
    def setupDimensions(self):
        self.width= Node.WIDTH
        self.height= Node.HEIGHT
        return


    def setupPrimitives(self, nodePolicy):

        NodeModule.Node.setupPrimitives(self, nodePolicy)

        font = nodePolicy.visualPolicy().font(
            VisualPolicyModule.VisualPolicy.KEY_FONT_DEFAULT)

        # TODO: 
        # consolidate code that creates a new label
        executeLabel = TextModule.zglText()
        executeLabel.position = nodePolicy.getPositionForExecuteStatusLabel()
        executeLabel.size = [self.width, self.height, 0]
        executeLabel.horizontal_align = nodePolicy.getHorizontalAlignmentOfLabel()
        executeLabel.vertical_align = nodePolicy.getVerticalAlignmentOfLabel()
        executeLabel.font = font
        # TODO:
        # this text should be dependent upon
        # whether there's a task associated with it
        executeLabel.text = "Uninitialized"
        self.parts[Node.PART_EXECUTE_STATUS] = executeLabel

        self.setupImageMap(nodePolicy)

        return

    def getImageParameterSweep(self):
        return 'ps unselected.png'
        

    def getParameterSweepImage(self):
        return 'ps unselected.png'
    
    def getImageSelectedFile(self):
        return 'node selected.png'

    def getImageNotSelectedFile(self):
        return 'node unselected.png'

    def setupImageMap(self, nodePolicy):
        self._setupImageMap(nodePolicy)
        self.setImageSelected(False)
        return


    def setImageParameterSweep(self, isParameterSweep):
        imageMap = self.parts[Node.PART_DISPLAY_IMAGES]

        imageMap[IMAGE_PARAMETER_SWEEP].visible(isParameterSweep)
        return

    def setImageSelected(self, isSelected):
        imageMap = self.parts[Node.PART_DISPLAY_IMAGES]

        imageMap[IMAGE_SELECTED_TRUE].visible(isSelected)
        imageMap[IMAGE_SELECTED_FALSE].visible(not isSelected)
            
        return


    def _setupImageMap(self, nodePolicy):

        self.shouldUpdateImage(True)
        self.shouldUpdateColours(False)

        contextManager = nodePolicy.contextManager()
        app = contextManager.app()

        imageSelectedPath = os.path.join(contextManager.imagePath(),
                                         self.getImageSelectedFile())
        imageNotSelectedPath = os.path.join(contextManager.imagePath(),
                                            self.getImageNotSelectedFile())
        imageParameterSweepPath = os.path.join(contextManager.imagePath(),
                                           self.getParameterSweepImage())
        
        imageSelected = self.createBackgroundPrimitive()
        imageSelected.setTextureImageFile(imageSelectedPath, mode='RGBA')

        imageNotSelected = self.createBackgroundPrimitive()
        imageNotSelected.setTextureImageFile(imageNotSelectedPath, mode='RGBA')

        size = self.getBounds()
        diffX = size[0]/12.0
        diffY = -1*diffX
        imageParameterSweep = self.createBackgroundPrimitive(size=size)
        imageParameterSweep.setTextureImageFile(imageParameterSweepPath, mode='RGBA')
        # NOTE:
        # this is a hack to get the PS image drawing
        imageParameterSweep.offsetPosition = (diffX, diffY, 0)

        # now specify the images for selected/unselected
        imageMap = {
            IMAGE_SELECTED_TRUE:imageSelected,
            IMAGE_SELECTED_FALSE:imageNotSelected,
            IMAGE_PARAMETER_SWEEP:imageParameterSweep
        }

        self.parts[Node.PART_DISPLAY_IMAGES] = imageMap
        self.parts[Node.PART_BACKGROUND].visible(False)

        generator = TaskModule.getTaskGeneratorForDefinition(self.nodeData)
        isParameterSweep = isinstance(
            generator, TaskModule.ParameterSweepTaskGenerator)
        self.setImageParameterSweep(isParameterSweep)
        
        return


    def updateExecuteStatus(self, status):

        executeLabel = self.parts[Node.PART_EXECUTE_STATUS]
        executeLabel.text = status

        # reset the cached values
        # so that they will be recached
        if hasattr(self, '_children'):
            delattr(self, '_children')

        return


    def getSelectionContextualMenu(self, event, eventHandler, canvas, selection):
        import menu as MenuModule
        popupMenu = MenuModule.NodeContextualMenu(
            event, eventHandler, canvas, selection)
        return popupMenu

    def updateImage(self):
        self.setImageSelected(self.isSelected())
        return

    # END class Node
    pass


class NestNode(Node):


    def getImageSelectedFile(self):
        return 'nest selected.png'

    def getImageNotSelectedFile(self):
        return 'nest unselected.png'

    # END class NestNode
    pass


class BranchNode(Node):

    # TODO:
    # implement the generation of the branch node image
    # and have this class return that value
    
    # END class BranchNode
    pass


class LoopNode(Node):

    # TODO:
    # implement the generation of the loop node image
    # and have this class return that value
    
    # END class LoopNode
    pass


class Edge(EdgeModule.Edge):


    def __init__(self, dataPath, guiPath):
        EdgeModule.Edge.__init__(self, None)
        self._dataPath = dataPath
        self.guiPath = guiPath
        return


    def inputPort(self):
        return self.guiPath[1]

    def outputPort(self):
        return self.guiPath[-2]

    def inputNode(self):
        return self.guiPath[0]

    def outputNode(self):
        return self.guiPath[-1]


    # END class Edge
    pass


class Port(PortModule.Port):

    def createBackgroundPrimitive(self, portPolicy):
        
        dataNode = self.node.nodeData
        contextManager = portPolicy.contextManager()
        parameterId = self.name
        
        parameter = dataNode.getParameter(parameterId)

        background = None
        if self.dataType == ParameterModule.PORT_TYPE_TEMPORAL:
            background = PrimitivesModule.zglTriangle()
            pass
        else:
            background = PrimitivesModule.zglEllipse()
            pass
        
        background.position = [0, 0, 0]
        background.size = [self.width, self.height, 1.0]
        background.corner_mode = True
        
        background.colour = None
        background.borderColour = [0.5, 0.5, 0.0, 1.0]
        
        return background
    
    
    def getSelectionContextualMenu(self, event, eventHandler, canvas, selection):
        import menu as MenuModule
        popupMenu = MenuModule.PortContextualMenu(
            event, eventHandler, canvas, selection)
        return popupMenu

    def OnDragRelease(self, event, canvas=None, 
                      objects=None,
                      eventHandler=None):
        
        edgePath = PortModule.Port.OnDragRelease(
            self, event, canvas=canvas,
            objects=objects, eventHandler=eventHandler)

        if edgePath is not None:

            contextManager = canvas.contextManager()

            #import pomsets_app.gui.event as EventModule
            #guiEvent = EventModule.EdgeCreatedEvent(
            #    path=edgePath)
            #contextManager.postEvent(guiEvent)

        return edgePath

    
    def initialSetup(self):
        
        dataNode = self.node.nodeData
        parameterId = self.name
        parameter =dataNode.getParameter(parameterId)
        self.dataType = parameter.portType()
        
        return
    


    # END class Port
    pass
