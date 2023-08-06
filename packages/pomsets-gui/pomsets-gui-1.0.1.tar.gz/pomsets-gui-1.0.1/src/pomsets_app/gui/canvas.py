import functools
import logging

import OpenGL
from OpenGL.GL import *
from OpenGL.GLUT import *

from zgl.zglUtils import zglUtils
import zgl_graphdrawer.application as ApplicationModule
import zgl_graphdrawer.canvas.gl_canvas as CanvasModule

import pypatterns.filter as FilterModule

import pypatterns.relational as RelationalModule
import pomsets.resource as ResourceModule

import pomsets.definition as DefinitionModule
import pomsets.task as TaskModule
import pomsets.parameter as ParameterModule

import pomsets_app.gui.graph as GraphModule


class Canvas(CanvasModule.Canvas, ResourceModule.Struct):
    
    ATTRIBUTES = [
        'nodeTable',
    ]


    def __init__(self, *args, **kwds):
        ResourceModule.Struct.__init__(self)
        CanvasModule.Canvas.__init__(self, *args, **kwds)
        self._frameIsInProcessOfShowing = False
        return


    def initGL(self):
        import platform
        if platform.system() in ['Linux']:
            glutInit([])
        return CanvasModule.Canvas.initGL(self)


    def resetNodeTable(self):
        table = RelationalModule.createTable(
            'node table',
            ['data', 'gui']
        )
        self.nodeTable(table)
        return

    def _getFilterForDataNode(self, node):
        filter = RelationalModule.ColumnValueFilter(
            'data',
            FilterModule.IdentityFilter(node)
        )
        return filter

    def hasGuiObjectForDataNode(self, node):
        filter = self._getFilterForDataNode(node)
        guiNodes = RelationalModule.Table.reduceRetrieve(
            self.nodeTable(),
            filter,
            ['gui']
        )
        if len(guiNodes) is 0:
            return False
        return True


    def getGuiObjectForDataNode(self, node):
        """
        should be able to use getGuiObjectForDataObject
        """

        filter = self._getFilterForDataNode(node)
        guiNodes = RelationalModule.Table.reduceRetrieve(
            self.nodeTable(),
            filter,
            ['gui']
        )
        if len(guiNodes) is 0:
            raise KeyError('no gui object found for node %s' % node.id())
        if len(guiNodes) is not 1:
            raise ValueError('expected only 1 gui object for node %s' % node.id())
        return guiNodes[0]


    def resetDrawables(self):
        CanvasModule.Canvas.resetDrawables(self)
        
        # the check here is because
        # this is also being called in the constructor
        if self.nodeTable() is not None:
            self.nodeTable().clear()
        else:
            self.resetNodeTable()
        
        return
    
    
    def addDrawable(self, drawable):
        CanvasModule.Canvas.addDrawable(self, drawable)

        # is it possible for the code that draws the nodes
        # to simply iterate over the rows of the table?
        if isinstance(drawable, GraphModule.Node):
            logging.debug("adding node %s to self.nodeTable()" % drawable.nodeData.name())
            row = self.nodeTable().addRow()
            row.setColumn('data', drawable.nodeData)
            row.setColumn('gui', drawable)
            pass

        pass


    def removeDrawable(self, drawable):
        if isinstance(drawable, GraphModule.Node):
            filter = RelationModule.ColumnValueFilter(
                'gui',
                FilterModule.IdentityFilter(drawable))
            self.nodeTable().removeRows(filter)
            pass

        CanvasModule.Canvas.removeDrawable(self, drawable)
        return


    def getResourceKeyForNode(self, dataNode):

        # TODO:
        # return the appropriate key
        # for the composite node,
        # e.g. nest, parameter sweep, loop, branch

        if not dataNode.isAtomic():
            generator = TaskModule.getTaskGeneratorForDefinition(dataNode)
            if isinstance(generator, TaskModule.NestTaskGenerator):
                return 'gui nest node class'
            #if isinstance(generator, TaskModule.ParameterSweepTaskGenerator):
            #    return 'gui parameter sweep node class'
            if isinstance(generator, TaskModule.LoopTaskGenerator):
                return 'gui loop node class'
            if isinstance(generator, TaskModule.BranchTaskGenerator):
                return 'gui branch node class'
            pass

        # default to generic node
        retVal = CanvasModule.Canvas.getResourceKeyForNode(self, dataNode)
        return retVal

    
    def hasCanvasPosition(self, dataNode):
        guiOptions = dataNode.guiOptions()
        return 'canvas position' in guiOptions
    
    def computeLayout(self):
        CanvasModule.Canvas.computeLayout(self)
        for uiNode in self.nodes:
            dataNode = uiNode.nodeData
            dataNode.guiOptions()['canvas position'] = uiNode.getPosition()
        return


    def updateExecutionStatus(self, task):
        # TODO:
        # this needs to handle the case that the task
        # is not pointing to the nest definition 
        # being displayed

        for uiNode in self.nodes:
            dataNode = uiNode.nodeData

            filter = task._getFilterForDefinition(dataNode)
            statusList = RelationalModule.Table.reduceRetrieve(
                task.tasksTable(),
                filter, ['status'], [])

            # update only if there's a status to update
            if not len(statusList):
                continue
            uiNode.updateExecuteStatus(statusList[0])
            pass

        self.updateGL()
        return

    def displayPomset(self, pomset):

        shouldComputeLayout = True
        shouldQueryUser = False
        
        # TODO:
        # determine if should query user
        self.resetDrawables()
        for dataNode in pomset.nodes():
            uiNode = self.addNode(dataNode)
            if self.hasCanvasPosition(dataNode):
                shouldComputeLayout = False
                x, y = dataNode.guiOptions()['canvas position']
                uiNode.setPosition(x, y)
            else:
                shouldQueryUser = True
            pass
        if self.contextManager().hasTaskForPomset(pomset):
            task = self.contextManager().getTaskForPomset(pomset)
            self.updateExecutionStatus(task)
        
        for dataPath in pomset.parameterConnectionPathTable().retrieve(
            FilterModule.TRUE_FILTER, 
            ['source node', 'source parameter',
             'target parameter', 'target node']):

            self.addEdge(dataPath)
            pass

        if shouldQueryUser and not shouldComputeLayout:
            print "should query user for auto arrange"
            # TODO:
            # if user confirms auto-arrange
            # set shouldComputeLayout to True

        # TODO:
        # call computeLayout only if the loaded pomset
        # does not already contain information about node positioning
        # self.computeLayout()
        if shouldComputeLayout:
            self.computeLayout()


        return



    def breadCrumbs(self, value=None):
        if value is not None:
            self._breadCrumbs = value
        if not hasattr(self, '_breadCrumbs'):
            self._breadCrumbs = 'No active pomset to display'
        return self._breadCrumbs


    def setSelection(self, selected):

        oldSelection = self.getSelection()
        self._selected = selected

        self.selectionChanged(oldSelection, self._selected)

        return

    def addToSelection(self, selected):

        self._selected.extend(selected)

        self.selectionChanged([], self._selected)
        pass


    def selectionChanged(self, oldSelection, newSelection):
        for object in oldSelection:
            if object not in newSelection and object.isSelectable():
                # The object was removed from selection
                object.isSelected(False)

                # self.nodePolicy().updateNode(object)
                object.shouldUpdateDisplay(True)


        for object in newSelection:
            if object not in oldSelection and object.isSelectable():
                # The object was added to the selection
                object.isSelected(True)

                # This code assumes selection is a node
                # which for now is true but may not be in the future
                #self.nodes.remove(object)
                #self.nodes.append(object)
                
                # self.nodePolicy().updateNode(object)
                object.shouldUpdateDisplay(True)
            pass

        return

        
    # END class Canvas
    pass




