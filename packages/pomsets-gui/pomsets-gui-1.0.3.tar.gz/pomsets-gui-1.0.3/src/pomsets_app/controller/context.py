from __future__ import with_statement

import copy
import logging
import os
import pickle
import shutil
import user
import uuid

import zgl_graphdrawer.GraphDrawerManager as ContextManagerModule


import pypatterns.command as CommandPatternModule

import pypatterns.filter as FilterModule
import pypatterns.relational as RelationalModule

import pomsets.builder as BuilderModule
import pomsets.command as ExecuteCommandModule
import pomsets.context as ContextModule
import pomsets.definition as PomsetDefinitionModule
import pomsets.library as DefinitionLibraryModule
import pomsets.error as ExecuteErrorModule
import pomsets.parameter as ParameterModule
import pomsets.resource as ResourceModule
import pomsets.task as TaskModule

import cloudpool.shell as ShellModule

import pomsets_app.controller.automaton as AutomatonModule



class ContextManager(ContextManagerModule.ContextManager, 
                     ResourceModule.Struct):

    ATTRIBUTES = [
        'app',
        'automaton',
        'eventHandlers',
        'taskTable',
        'activeLibrary',
        'persistentLibrary',
        'transientLibrary',
        'pomsetBuilder'
    ]

    COLUMNS_VIRTUALMACHINE_DISPLAY = [
        'Service', 'Instance ID', 'Image ID', 
        'IP', 'Key name', 'Enabled'
    ]

    def __init__(self):
        ContextManagerModule.ContextManager.__init__(self)
        ResourceModule.Struct.__init__(self)

        self.eventHandlers([])

        table = RelationalModule.createTable(
            'tasks',
            ['task', 'pomset']
        )
        self.taskTable(table)

        self.activePomsetContext(None)

        self.pomsetBuilder(BuilderModule.Builder())
        return


    def addActivePomsetContext(self, pomsetContext):
        self.activeLibrary().addPomsetContext(pomsetContext)
        self.activePomsetContext(pomsetContext)
        return

    def activePomset(self):
        activePomsetContext = self.activePomsetContext()
        if activePomsetContext is None:
            return None
        return activePomsetContext.pomset()
    
    def activePomsetContexts(self):
        filter = FilterModule.TRUE_FILTER
        activePomsetContexts = RelationalModule.Table.reduceRetrieve(
            self.activeLibrary().definitionTable(), filter, ['context'], [])
        return activePomsetContexts
    
    
    def activePomsetContext(self, value=None):
        if value is not None:
            self._activePomsetContext = value
        if not hasattr(self, '_activePomsetContext'):
            self._activePomsetContext = None
        return self._activePomsetContext
    
    
    def initializeAutomaton(self, automaton):

        self.automaton(automaton)
        automaton.contextManager(self)

        return


    def initializeEventHandlers(self):
        ContextManagerModule.ContextManager.initializeEventHandlers(self)

        for key in ['canvas event handler',
                    'mouse event handler',
                    'key event handler']:
            
            eventHandler = self.app().getResourceValue(key)
            self.eventHandlers().append(eventHandler)
            eventHandler.contextManager = lambda: self
            pass

        return



    def postEvent(self, event):


        for eventHandler in self.eventHandlers():
            eventHandler.AddPendingEvent(event)
            return

        return

    def createNewPomset(self, *args, **kwds):
        return self.pomsetBuilder().createNewNestPomset(*args, **kwds)


    def createNewNode(self, **kwds):
        return self.pomsetBuilder().createNewNode(
            self.activePomset(), **kwds)

    def canConnect(self, port1, port2):
        port1Data = (port1.node.nodeData, port1.name)
        port2Data = (port2.node.nodeData, port2.name)
        return self.pomsetBuilder().canConnect(
            self.activePomset(),
            port1Data[0], port1Data[1],
            port2Data[0], port2Data[1])



    def connect(self, port1, port2):

        sourceNode = port1.node.nodeData
        sourceParameterId = port1.name
        targetNode = port2.node.nodeData
        targetParameterId = port2.name
        return self.pomsetBuilder().connect(
            self.activePomset(),
            sourceNode, sourceParameterId,
            targetNode, targetParameterId)


    def initializeLibraries(self):
        
        # TODO:
        # pull the bootstrapDefinitionDir from the config file instead

        appConfigDir = self.getAppConfigDir()
        bootstrapDefinitionDir = os.path.join(appConfigDir, 'library')
        
        # ensure that the pomset directories exists
        if not os.path.exists(bootstrapDefinitionDir):

            # TODO:
            # once we've migrated to 2.6
            # we can use the keyword "ignore"
            # to pass in a callable to copytree, 
            # so that we don't need to call rmtree

            defaultInitialLibrary = os.path.join(self.resourcePath(), 'library')
            # now copy the default initial library files over
            shutil.copytree(defaultInitialLibrary, bootstrapDefinitionDir)
            # remove the svn dir
            svnDir = os.path.sep.join([bootstrapDefinitionDir, '.svn'])
            if os.path.exists('.svn'):
                shutil.rmtree(svnDir)
            pass
        
        library = DefinitionLibraryModule.Library()
        library.bootstrapLoaderDefinitionsDir(bootstrapDefinitionDir)
            
        library.loadBootstrapLoaderDefinitions()
        self.persistentLibrary(library)
        
        library = DefinitionLibraryModule.Library()
        self.transientLibrary(library)

        library = DefinitionLibraryModule.Library()
        self.activeLibrary(library)

        return 

    def getContextForDefinition(self, definition, library=None):
        if library is None:
            library = self.transientLibrary()

        filter = RelationalModule.ColumnValueFilter(
            'definition',
            FilterModule.IdentityFilter(definition)
            )
        contexts = RelationalModule.Table.reduceRetrieve(
            library.definitionTable(),
            filter,
            ['context'],
            [])
        if len(contexts) is 0:
            raise ValueError('no context found for definition %s in library' % definition.name())
        if len(contexts) is not 1:
            raise ValueError('more than one context found for definition %s in library' % definition.name())
        return contexts[0]

        
    def getLoadedDefinitions(self):
        definitionTable = self.transientLibrary().definitionTable()
        for definitionRow in definitionTable.retrieve(
            columns=['context']):
            
            yield definitionRow[0]
        raise StopIteration
    
    
    def getLibraryDefinitions(self):
        
        definitionTable = self.persistentLibrary().definitionTable()
        for definitionRow in definitionTable.retrieve(
            columns=['context']):
            
            yield definitionRow[0]
        raise StopIteration
    

    def outputCommandsToStream(self, stream):
        # need to execute the pomset, 
        # with the exception that the execution
        # is actually to write to a stream
        # and that files should not be staged

        env = ExecuteCommandModule.PrintTaskCommand()
        env.prefix('# ')
        env.postfix('\n\n')

        env.outputStream(stream)

        # TODO;
        # if there are no threads allocated
        # then need to create a new thread
        # will also need to ensure 
        # that we remove the thread later

        # copy the active pomset
        # so that we don't screw with the active one
        # in case that it's already executing
        pomset = copy.copy(self.activePomset())

        commandBuilder = ExecuteCommandModule.CommandBuilder(
            ExecuteCommandModule.buildCommandFunction_commandlineArgs
        )
        commandBuilderMap = {
            'print task':commandBuilder,
            'shell process':commandBuilder
        }

        requestKwds = self.generateRequestKwds(
            executeEnvironment = env,
            executeEnvironmentId = AutomatonModule.ID_EXECUTE_LOCAL,
            commandBuilderMap = commandBuilderMap)
        self.executePomset(
            pomset = pomset,
            requestKwds=requestKwds,
            shouldWait = True)

        # remove the task for the pomset
        # from the task table
        # because we want to still be able to execute it
        # although it probably doesn't matter
        # because we're copying the pomset above anyway
        filter = RelationalModule.ColumnValueFilter(
            'pomset',
            FilterModule.IdentityFilter(pomset)
        )
        self.taskTable().removeRows(filter)

        return


    def _getTasksForPomset(self, pomset):
        filter = RelationalModule.ColumnValueFilter(
            'pomset',
            FilterModule.IdentityFilter(pomset)
        )
        tasks = RelationalModule.Table.reduceRetrieve(
            self.taskTable(),
            filter,
            ['task'],
            []
        )
        return tasks


    def hasTaskForPomset(self, pomset):
        tasks = self._getTasksForPomset(pomset)
        return len(tasks) is not 0


    def getTaskForPomset(self, pomset):
        tasks = self._getTasksForPomset(pomset)
        if len(tasks) > 1:
            raise NotImplemented('not implemented for %s tasks' % len(tasks))
        return tasks[0]


    def getDefaultCommandBuilderMap(self):
        return {}


    def generateRequestKwds(self, 
                            executeEnvironment=None,
                            executeEnvironmentId=None,
                            commandBuilderMap=None):


        if not any([executeEnvironment, executeEnvironmentId]):
            raise NotImplementedError(
                'need to specify an execute environment or environment id')

        # make a copy of the defaultCommandBuilderMap
        # and overlay values from the map being passed in
        defaultMap = copy.copy(self.getDefaultCommandBuilderMap())
        if commandBuilderMap is not None:
            defaultMap.update(commandBuilderMap)
        commandBuilderMap = defaultMap

        kwds = {
            'command builder map':commandBuilderMap,
            'execute environment':executeEnvironment,
            'execute environment id':executeEnvironmentId,
            'worker thread configures execute environment':(executeEnvironmentId is not None and executeEnvironment is None)
            }
        return kwds


    def executePomset(self, pomset=None, requestKwds=None, shouldWait=False):

        # TODO:
        # first check to see if there's already a task
        # associated with the active pomset
        if self.hasTaskForPomset(pomset):
            raise ExecuteErrorModule(
                'there is already a task for the active pomset')
        

        # associate the task with the 
        # active pomset in the tasks table
        # need to do this before we execute
        # in case the execution errors
        task = TaskModule.CompositeTask()
        row = self.taskTable().addRow()
        row.setColumn('task', task)
        row.setColumn('pomset', pomset)


        self.automaton().executePomset(
            task=task,
            pomset=pomset, 
            requestKwds=requestKwds,
            shouldWait=shouldWait)


        return task


    def closeActivePomset(self):
        # TODO:
        # need to ensure that the task is no longer running

        self.closePomset(self.activePomsetContext())
        return
        
    
    def closePomset(self, pomsetContextToClose):

        # TODO:
        # similar to the add, this should be a command

        # remove from contextManager.taskTable
        filter = RelationalModule.ColumnValueFilter(
            'pomset',
            FilterModule.IdentityFilter(pomsetContextToClose.pomset())
        )
        self.taskTable().removeRows(filter)

        filter = RelationalModule.ColumnValueFilter(
            'context',
            FilterModule.IdentityFilter(pomsetContextToClose))
        self.activeLibrary().removeDefinition(filter)

        # TODO:
        # if there's another pomset open
        # then we should use that one
        # as the active pomset instead
        try:
            row = self.activeLibrary().definitionTable().retrieve(columns=['context']).next()
            self.activePomsetContext(row[0])
        except StopIteration:
            # there is no more active pomset context
            self._activePomsetContext = None

            pass

        return

    
    def imagePath(self):
        return os.path.join(self.resourcePath(), 'images')


    def getExecutableTypes(self):
        return ['Shell', 'Hadoop Jar', 'Hadoop Streaming', 'Hadoop Pipes']


    def getTypeForExecutable(self, executable):

        if executable.__class__ is ExecuteCommandModule.Executable:
            return 'Shell'

        import pomsets.hadoop as HadoopModule
        if executable.__class__ is HadoopModule.JarExecutable:
            # TODO:
            # need to inspect the jarFile
            jarFile = ' '.join(executable.jarFile())
            if jarFile == self.getHadoopStreamingJar():
                return 'Hadoop Streaming'

            return 'Hadoop Jar'

        if executable.__class__ is HadoopModule.PipesExecutable:
            return 'Hadoop Pipes'

        raise NotImplementedError(
            'not implemented for executable clas %s' % executable.__class)


    def getClassForExecutableType(self, executableType):
        if executableType in ['Shell']:
            return ExecuteCommandModule.Executable

        import pomsets.hadoop as HadoopModule
        if executableType in ['Hadoop Jar', 'Hadoop Streaming']:
            return HadoopModule.JarExecutable

        if executableType in ['Hadoop Pipes']:
            return HadoopModule.PipesExecutable

        raise NotImplementedError(
            'not implemented for executable type %s' % executableType)


    def getHadoopStreamingJar(self):
        configuration = self.automaton().hadoopConfigurations()['localhost']
        return configuration['streaming jar']


    # END class ContextManager
    pass



class QtContextManager(ContextManager):

    ATTRIBUTES = ContextManager.ATTRIBUTES + [
        'currentDisplayedPomsetInfo',
        'mainWindow'
        ]

    def getAppConfigDir(self):
        import user
        appConfigDir = os.path.join(user.home, '.pomsets')
        return appConfigDir

    def initializeEventHandlers(self):
        return

    # END class QtContextManager
    pass
