import os

import zgl_graphdrawer.LayoutPolicy as LayoutPolicyModule
import zgl_graphdrawer.NodePolicy as NodePolicyModule
import zgl_graphdrawer.VisualPolicy as VisualPolicyModule

import pomsets_app.gui.graph as GraphModule

class NodePolicy(NodePolicyModule.SimpleNodePolicy):

    def __init__(self, *args, **kwds):
        NodePolicyModule.SimpleNodePolicy.__init__(self, *args, **kwds)
        return
    
    def getPositionForNameLabel(self):
        return [0, 10, 0]

    def getPositionForExecuteStatusLabel(self):
        return [0, -10, 0]
    
    # END class NodePolicy
    pass

class VisualPolicy(VisualPolicyModule.VisualPolicy):
    
    def getFontPath(self):
        return os.sep.join([self.contextManager().resourcePath(),
                            'fonts'])
    
    # END class VisualPolicy
    pass

class BasicLayoutPolicy(LayoutPolicyModule.LayoutPolicy):

    OFFSET_X = 100
    OFFSET_Y = 100

    def layoutNodes(self, nodes, edges):

        # sort the nodes
        predecessorMap = {}
        successorMap = {}
        for edge in edges:
            sourceNode = edge.sourceNode()
            targetNode = edge.targetNode()
            if not targetNode in predecessorMap:
                predecessorMap[targetNode] = []
                pass
            predecessorMap[targetNode].append(sourceNode)
            if not sourceNode in successorMap:
                successorMap[sourceNode] = []
            successorMap[sourceNode].append(targetNode)
            pass

        minimalNodes = set(nodes).difference(
            set(reduce(list.__add__, successorMap.values(), [])))
        nodeToLevelMap = dict([(x,0) for x in minimalNodes])

        processedNodes = set(minimalNodes)
        nodesToProcess = reduce(
            list.__add__,
            [successorMap[x] for x in minimalNodes], [])
        while len(nodesToProcess):
            nodeToProcess = nodesToProcess.pop(0)
            processedNodes.add(nodeToProcess)

            # add the node's successors to nodesToProces
            nodesToProcess.extend(successorMap.get(nodeToProcess, []))

            nodePredecessors = predecessorMap.get(nodeToProcess, [])
            unprocessedPredecessors = set(nodePredecessors).difference(processedNodes)
            if len(unprocessedPredecessors) is not 0:
                # we have not processed all its predecessors,
                # so we don't do anything
                continue
            nodeToLevelMap[nodeToProcess] = max(
                [nodeToLevelMap[x] for x in nodePredecessors]) + 1
            pass
        
        # place the nodes into the different levels
        levelToNodeMap = {}
        for node, level in nodeToLevelMap.iteritems():
            if not level in levelToNodeMap:
                levelToNodeMap[level] = []
            levelToNodeMap[level].append(node)

        # now set the position accordingly
        numLevels = len(levelToNodeMap)

        offsetX = GraphModule.Node.WIDTH + 50
        offsetY = GraphModule.Node.HEIGHT + 50

        height = offsetY * numLevels
        width =  offsetX * max([len(x) for x in levelToNodeMap.values()])
        for level, nodesInLevel in levelToNodeMap.iteritems():
            y = offsetY * (numLevels - level - 1) + BasicLayoutPolicy.OFFSET_Y 
            for index, nodeInLevel in enumerate(nodesInLevel):
                x = offsetX * index + BasicLayoutPolicy.OFFSET_X
                nodeInLevel.setPosition(x, y)
            pass

        return (width, height)


    # END class LayoutPolicy
    pass


class GraphvizLayoutPolicy(LayoutPolicyModule.GraphVizLayoutPolicy):

    def generateDotFile(self, path, nodes, edges):

        import gv
        
        nodeMap = {}

        gvGraph = gv.digraph('name')
        for node in nodes:
            gvNode = gv.node(gvGraph, node.nodeData.name())
            nodeMap[node] = gvNode
            gv.setv(gvNode, 'pos', str(node.getPosition()))

        for edge in edges:
            gvEdge = gv.edge(gvGraph, 
                             edge.sourceNode().nodeData.name(),
                             edge.targetNode().nodeData.name())

        gv.write(gvGraph, path)
        return


    # END class GraphvizLayoutPolicy
    pass
