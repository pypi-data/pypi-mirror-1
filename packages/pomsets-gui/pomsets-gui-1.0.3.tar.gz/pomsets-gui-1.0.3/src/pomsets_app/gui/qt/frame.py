import functools
import logging
import os
import platform
import sys
import uuid

import numpy

from PyQt4 import QtGui
from PyQt4.QtCore import *
from PyQt4.QtOpenGL import *


import pypatterns.relational as RelationalModule
import pypatterns.filter as FilterModule

import pomsets.context as ContextModule
import pomsets.library as LibraryModule

import pomsets_app.utils as AppUtilsModule
import pomsets_app.controller.automaton as AutomatonModule
import pomsets_app.gui.frame as FrameModule
import pomsets_app.gui.utils as GuiUtilsModule
import pomsets_app.gui.qt.canvas as CanvasModule
import pomsets_app.gui.qt.menu as MenuModule
import pomsets_app.gui.qt.pomset_tree.widget as PomsetTreeModule


class Frame(QtGui.QMainWindow, FrameModule.Frame):

    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        self.setMinimumSize(800, 600)
        self._widgets = {}
        return

    def putWidget(self, name, widget):
        self._widgets[name] = widget
        return

    def getWidget(self, name):
        return self._widgets[name]


    def initializeMenuBar(self):
        menuBar = self.menuBar()

        pomsetMenu = menuBar.addMenu('Pomsets')
        newPomsetAction = pomsetMenu.addAction('New')
        loadPomsetAction = pomsetMenu.addAction('Load')
        savePomsetAction = pomsetMenu.addAction('Save')
        savePomsetAsAction = pomsetMenu.addAction('Save as')
        closePomsetAction = pomsetMenu.addAction('Close')
        self.connect(newPomsetAction,
                     SIGNAL('triggered()'), self.OnCreateNewTopLevelPomset)
        self.connect(loadPomsetAction, 
                     SIGNAL('triggered()'), self.OnLoadTopLevelPomset)
        self.connect(savePomsetAction, 
                     SIGNAL('triggered()'), self.OnSaveCurrentActivePomset)
        self.connect(savePomsetAsAction, 
                     SIGNAL('triggered()'), self.OnSavePomset)
        self.connect(closePomsetAction, 
                     SIGNAL('triggered()'), self.OnCloseActivePomset)


        # we only do this if not a Mac
        # because on a mac, the exit and about menus
        # get added to the bar at the top of the windw
        if not platform.system() in ['Darwin']:
            pomsetMenu.addSeparator()
        exitApplicationAction = pomsetMenu.addAction('Exit')
        self.connect(exitApplicationAction, 
                     SIGNAL('triggered()'), self.OnExitApplication)

        
        # we only do this if not a Mac
        # because on a mac, the exit and about menus
        # get added to the bar at the top of the windw
        if not platform.system() in ['Darwin']:
            helpMenu = menuBar.addMenu('Help')
            aboutApplicationAction = helpMenu.addAction('About')
        else:
            aboutApplicationAction = pomsetMenu.addAction('About')
        self.connect(aboutApplicationAction, 
                     SIGNAL('triggered()'), self.OnAboutApplication)


        executionMenu = menuBar.addMenu('Execute')
        previewExecutionAction = executionMenu.addAction('Preview')
        executionMenu.addSeparator()
        localExecutionAction = executionMenu.addAction('Local')
        eucaExecutionAction = executionMenu.addAction('Eucalyptus')

        self.connect(previewExecutionAction, 
                     SIGNAL('triggered()'), self.OnExecutePreview)
        self.connect(localExecutionAction, 
                     SIGNAL('triggered()'), self.OnExecuteLocal)
        self.connect(eucaExecutionAction, 
                     SIGNAL('triggered()'), self.OnExecuteEucalyptus)


        configurationMenu = menuBar.addMenu('Configuration')
        cloudpoolAction = configurationMenu.addAction('Cloud pool')
        configurationMenu.addSeparator()
        euca2oolsAction = configurationMenu.addAction('Eucalyptus')
        hadoopAction = configurationMenu.addAction('Hadoop')

        self.connect(cloudpoolAction, 
                     SIGNAL('triggered()'), self.OnCloudPoolConfiguration)
        self.connect(euca2oolsAction, 
                     SIGNAL('triggered()'), self.OnEuca2oolsConfiguration)
        self.connect(hadoopAction, 
                     SIGNAL('triggered()'), self.OnHadoopConfiguration)

        return


    def initializeWidgets(self):

        self.initializeMenuBar()

        mainSplitterWidget = QtGui.QSplitter(self)

        librarySplitterWidget = QtGui.QSplitter(mainSplitterWidget)
        librarySplitterWidget.setOrientation(Qt.Vertical)

        activeLibraryTreeWidget = PomsetTreeModule.PomsetTreeWidget(librarySplitterWidget)
        activeLibraryTreeWidget.setHeaderLabels(['Active pomsets'])
        activeLibraryTreeWidget.setHeaderHidden(False)
        librarySplitterWidget.addWidget(activeLibraryTreeWidget)
        self.putWidget('active library tree', activeLibraryTreeWidget)

        toolbox = QtGui.QToolBox(librarySplitterWidget)
        toolbox.addItem(PomsetTreeModule.PomsetTreeWidget(toolbox), 'Loaded definitions')
        toolbox.addItem(PomsetTreeModule.PomsetTreeWidget(toolbox), 'Library definitions')
        toolbox.setCurrentIndex(1)
        librarySplitterWidget.addWidget(toolbox)

        canvas = CanvasModule.Canvas(mainSplitterWidget, 800, 600)
        canvas.contextManager(self.app().contextManager())
        canvas.resetDrawables()
        self.putWidget('graph canvas', canvas)
        self.canvas = canvas
        mainSplitterWidget.addWidget(canvas)

        self.setCentralWidget(mainSplitterWidget)

        # signal from popup menu to create node
        QObject.connect(
            toolbox.widget(0),
            SIGNAL("OnCreateNode(PyQt_PyObject,PyQt_PyObject,QPoint)"),
            self.OnCreateNode)
        QObject.connect(
            toolbox.widget(1), 
            SIGNAL("OnCreateNode(PyQt_PyObject,PyQt_PyObject,QPoint)"),
            self.OnCreateNode)
        
        # notify the widgets that a node got created
        QObject.connect(self, SIGNAL("OnNodeCreated(PyQt_PyObject,QPoint)"),
                        canvas.OnNodeCreated)
        QObject.connect(self, SIGNAL("OnNodeCreated(PyQt_PyObject,QPoint)"),
                        activeLibraryTreeWidget.OnRefresh)

        # notify the widgets that an edge got created
        QObject.connect(canvas, SIGNAL("OnEdgeCreated(PyQt_PyObject)"),
                        activeLibraryTreeWidget.OnRefresh)

        # notify the widgets that a node got moved
        QObject.connect(canvas, SIGNAL("OnNodesMoved()"),
                        activeLibraryTreeWidget.OnRefresh)

        # notify the widgets that a node got duplicated
        QObject.connect(self, SIGNAL("OnNodesDuplicated(PyQt_PyObject)"),
                        activeLibraryTreeWidget.OnRefresh)
        QObject.connect(self, SIGNAL("OnNodesDuplicated(PyQt_PyObject)"),
                        canvas.OnNodesDuplicated)

        # notify the widgets that a node got deleted
        QObject.connect(self, SIGNAL("OnNodesDeleted()"),
                        activeLibraryTreeWidget.OnRefresh)
        QObject.connect(self, SIGNAL("OnNodesDeleted()"),
                        canvas.OnRefresh)
        
        # notify the widget that a pomset got moved across libraries
        QObject.connect(self, SIGNAL("OnPomsetMoved()"),
                        toolbox.widget(0).OnRefresh)
        QObject.connect(self, SIGNAL("OnPomsetMoved()"),
                        toolbox.widget(1).OnRefresh)


        # notify the widget that a pomset got created
        QObject.connect(self, SIGNAL("OnPomsetCreated()"),
                        toolbox.widget(0).OnRefresh)
        QObject.connect(self, SIGNAL("OnPomsetCreated()"),
                        toolbox.widget(1).OnRefresh)
        QObject.connect(self, SIGNAL("OnPomsetCreated()"),
                        activeLibraryTreeWidget.OnRefresh)

        # notify the widget that a pomset got loaded
        QObject.connect(self, SIGNAL("OnPomsetLoaded(PyQt_PyObject)"),
                        toolbox.widget(0).OnRefresh)
        QObject.connect(self, SIGNAL("OnPomsetLoaded(PyQt_PyObject)"),
                        toolbox.widget(1).OnRefresh)
        QObject.connect(self, SIGNAL("OnPomsetLoaded(PyQt_PyObject)"),
                        activeLibraryTreeWidget.OnRefresh)

        # notify the widget that a pomset got saved
        QObject.connect(self, SIGNAL("OnPomsetSaved(PyQt_PyObject)"),
                        toolbox.widget(0).OnRefresh)
        QObject.connect(self, SIGNAL("OnPomsetSaved(PyQt_PyObject)"),
                        toolbox.widget(1).OnRefresh)
        QObject.connect(self, SIGNAL("OnPomsetSaved(PyQt_PyObject)"),
                        activeLibraryTreeWidget.OnRefresh)

        # notify the widget that a pomset was closed
        QObject.connect(self, SIGNAL("OnPomsetClosed(PyQt_PyObject)"),
                        toolbox.widget(0).OnRefresh)
        QObject.connect(self, SIGNAL("OnPomsetClosed(PyQt_PyObject)"),
                        toolbox.widget(1).OnRefresh)
        QObject.connect(self, SIGNAL("OnPomsetClosed(PyQt_PyObject)"),
                        activeLibraryTreeWidget.OnRefresh)

        # notify the widget that a pomset got modified
        QObject.connect(self, SIGNAL("OnPomsetModified(PyQt_PyObject)"),
                        toolbox.widget(0).OnRefresh)
        QObject.connect(self, SIGNAL("OnPomsetModified(PyQt_PyObject)"),
                        activeLibraryTreeWidget.OnRefresh)
        QObject.connect(self, SIGNAL("OnPomsetModified(PyQt_PyObject)"),
                        canvas.OnRefresh)

        # TODO:
        # notify that a pomset was submitted for execution

        # TODO:
        # notify that a pomset errored in execution

        # TODO:
        # notify a task execution status changed
        QObject.connect(self, SIGNAL("OnTaskExecutionStatusChanged()"),
                        canvas.updateGL)

        return


    def closeEvent(self, event):
        # call our own exit application function
        self.OnExitApplication()
        event.ignore()
        return


    def setWidgetDataSources(self):

        contextManager = self.app().contextManager()

        mainSplitterWidget = self.centralWidget()

        librarySplitterWidget = mainSplitterWidget.widget(0)
        toolboxWidget = librarySplitterWidget.widget(1)
        
        persistentLibraryTreeWidget = toolboxWidget.widget(1)
        
        persistentLibraryTreeWidget.pomsetLibrary(
            contextManager.persistentLibrary())
        persistentLibraryTreeWidget.emptyDataSourceString('None loaded')
        persistentLibraryTreeWidget.contextManager(contextManager)


        notBootstrapFilter = FilterModule.constructNotFilter()
        notBootstrapFilter.addFilter(
            LibraryModule.getBootstrapLoaderPomsetsFilter())
        persistentLibraryTreeWidget.pomsetFilter(notBootstrapFilter)
        persistentLibraryTreeWidget.shouldEnableDragToCanvas(True)
        persistentLibraryTreeWidget.contextualMenuClass(
            MenuModule.LibraryDefinitionContextualMenu)

        transientLibraryTreeWidget = toolboxWidget.widget(0)
        transientLibraryTreeWidget.contextManager(contextManager)
        transientLibraryTreeWidget.pomsetLibrary(
            contextManager.transientLibrary())
        transientLibraryTreeWidget.emptyDataSourceString('None loaded')
        transientLibraryTreeWidget.shouldIndicateModified(True)
        transientLibraryTreeWidget.shouldEnableDragToCanvas(True)
        transientLibraryTreeWidget.contextualMenuClass(
            MenuModule.LoadedDefinitionContextualMenu)

        activeLibraryTreeWidget = librarySplitterWidget.widget(0)
        activeLibraryTreeWidget.contextManager(contextManager)
        activeLibraryTreeWidget.pomsetLibrary(
            contextManager.activeLibrary())
        activeLibraryTreeWidget.emptyDataSourceString('None active')
        activeLibraryTreeWidget.shouldShowInternals(True)
        activeLibraryTreeWidget.shouldExpand(True)
        activeLibraryTreeWidget.shouldIndicateModified(True)
        activeLibraryTreeWidget.contextualMenuClass(
            MenuModule.ActivePomsetContextualMenu)
        activeLibraryTreeWidget.mouseDoubleClickCallback(
            functools.partial(activeLibraryTreeWidget.displayPomset,
                              frame=self))

        return

    def populateWidgets(self):

        mainSplitterWidget = self.centralWidget()

        librarySplitterWidget = mainSplitterWidget.widget(0)
        toolboxWidget = librarySplitterWidget.widget(1)

        widgets = [librarySplitterWidget.widget(0)] + \
            map(toolboxWidget.widget, range(toolboxWidget.count()))
            
        for widget in widgets:
            widget.populate()

        return


    def OnSaveCurrentActivePomset(self):
        contextManager = self.app().contextManager()
        pomsetContext, pomset = contextManager.currentDisplayedPomsetInfo()
        fileName = pomsetContext.url()
        self.OnSavePomset(pomsetContext, fileName)
        return

    def OnSavePomset(self, pomsetContext=None, fileName=None):
        contextManager = self.app().contextManager()

        if pomsetContext is None:
            pomsetContext, pomset = contextManager.currentDisplayedPomsetInfo()

        if fileName is None:
            import user
            fileName = QtGui.QFileDialog.getSaveFileName(
                self,
                QString("Save pomset"),
                QString(user.home),
                QString("Pomset workflows (*.pomset)"))

        if fileName and len(fileName):
            ContextModule.savePomsetAs(pomsetContext, str(fileName))
            self.emit(SIGNAL("OnPomsetSaved(PyQt_PyObject)"), pomsetContext)
            return True

        return False


    def OnLoadTopLevelPomset(self):

        contextManager = self.app().contextManager()
        pomsetContext = self.OnLoadPomsetIntoLibrary(
            contextManager.activeLibrary())
        if pomsetContext:
            contextManager.activePomsetContext(pomsetContext)
            self.displayPomset(pomsetContext)
            self.canvas.OnRefresh()
        return


    def OnLoadPomsetIntoLibrary(self, library, filter=None):
        import user
        fileName = QtGui.QFileDialog.getOpenFileName(
            self,
            QString("Load pomset"), 
            QString(user.home),
            QString("Pomset workflows (*.pomset)"))

        # TODO:
        # remove this hack that currently
        # allows us to prevent loading nest definitions
        if filter is None:
            filter = FilterModule.TRUE_FILTER

        pomsetContext = None
        if fileName and len(fileName):
            pomsetContext = ContextModule.loadPomset(path=fileName)
            if filter.matches(pomsetContext):
                library.addPomsetContext(pomsetContext)
                self.emit(SIGNAL("OnPomsetLoaded(PyQt_PyObject)"), 
                          pomsetContext)
            else:
                # TODO:
                # need to display an error message
                # to the user
                pass
            pass

        return pomsetContext

    def OnCreateNewTopLevelPomset(self):

        contextManager = self.app().contextManager()
        pomsetContext = contextManager.createNewPomset()
        contextManager.addActivePomsetContext(pomsetContext)
        self.displayPomset(pomsetContext)
        self.canvas.OnRefresh()
        self.emit(SIGNAL("OnPomsetCreated()"))
        return


    def OnCreateNewAtomicPomset(self):

        context = GuiUtilsModule.createDefinition(
            self.app().contextManager())
    
        self.emit(SIGNAL("OnPomsetCreated()"))
        return


    def OnCloseActivePomset(self, pomsetContext=None, 
                            shouldQueryIfModified=True):

        contextManager = self.app().contextManager()

        if pomsetContext is None:
            pomsetContext, pomset = contextManager.currentDisplayedPomsetInfo()

        # query the user to save the modification
        if pomsetContext.isModified() and shouldQueryIfModified:
            pomset = pomsetContext.pomset()
            pomsetName = pomset.name()

            msgBox = QtGui.QMessageBox(self)
            msgBox.setText("pomset \"%s\" has been modified." % pomsetName)
            msgBox.setInformativeText("Discard changes, save, or cancel close?")
            msgBox.setStandardButtons(
                QtGui.QMessageBox.Discard | 
                QtGui.QMessageBox.Save | 
                QtGui.QMessageBox.Cancel)
            msgBox.setDefaultButton(QtGui.QMessageBox.Cancel)
            ret = msgBox.exec_()

            if ret == QtGui.QMessageBox.Cancel:
                return
            if ret == QtGui.QMessageBox.Save:
                pomsetSaved = self.OnSavePomset(pomsetContext=pomsetContext, 
                                                fileName=pomsetContext.url())
                if not pomsetSaved:
                    # the user cancled the file dialog
                    # so we assume that they want to cancel the save
                    return
                pass
            if ret == QtGui.QMessageBox.Discard:
                # discard does nothing, 
                # we continue with the rest of this function
                pass

            pass

        contextManager.closePomset(pomsetContext)

        activeContext = contextManager.activePomsetContext()
        self.displayPomset(activeContext)
        self.canvas.OnRefresh()

        self.emit(SIGNAL("OnPomsetClosed(PyQt_PyObject)"), pomsetContext)
        return


    def OnDuplicateNodes(self, nodes):

        contextManager = self.app().contextManager()

        pomsetContext, pomset = contextManager.currentDisplayedPomsetInfo()

        nodeMap = {}
        for guiNode in nodes:
            dataNode = guiNode.nodeData
            copyDataNode = contextManager.pomsetBuilder().copyNode(
                pomset, dataNode)
            copyDataNode.name('copy of ' + dataNode.name())

            nodeMap[copyDataNode] = dataNode
            
            pass

        self.emit(SIGNAL("OnNodesDuplicated(PyQt_PyObject)"), nodeMap)
        return



    def OnDeleteNodes(self, nodes):
        contextManager = self.app().contextManager()
        pomsetContext, pomset = contextManager.currentDisplayedPomsetInfo()

        for guiNode in nodes:
            dataNode = guiNode.nodeData
            contextManager.pomsetBuilder().removeNode(
                pomset, dataNode)
        self.emit(SIGNAL("OnNodesDeleted()"))
        return


    def OnCreateNode(self, pomsetContext, pomset, pos, name=None):

        contextManager = self.app().contextManager()

        if name is None:
            # create a node
            # set its position
            name = '%s_%s' % (pomset.name() or "anonymous",
                              uuid.uuid4().hex[:3])

        node = contextManager.createNewNode(
            name=name, definitionToReference=pomset)

        pomsetContext.isModified(True)

        # emit a signal
        # so that the other widgets
        # will receive it and update accordingly
        self.emit(SIGNAL("OnNodeCreated(PyQt_PyObject,QPoint)"), node, pos)

        return


    def OnMoveDefinitionToLibrary(self, pomsetContext):
        contextManager = self.app().contextManager()
        persistentLibrary = contextManager.persistentLibrary()
        transientLibrary = contextManager.transientLibrary()
        definition = pomsetContext.pomset()

        # backup the existing library
        AppUtilsModule.backupLibrary(
            persistentLibrary.bootstrapLoaderDefinitionsDir())
        
        definitionFilter = RelationalModule.ColumnValueFilter(
            'definition',
            FilterModule.IdentityFilter(definition)
        )
        
        # remove from transient library
        transientLibrary.removeDefinition(definitionFilter)

        # define the url for the definition
        definitionPath = definition.id() + '.pomset'
        definition.url(definitionPath)
        outputDir = persistentLibrary.bootstrapLoaderDefinitionsDir()
        
        # save out the definition
        ContextModule.pickleDefinition(
            os.path.join(outputDir, definitionPath), definition)
        
        # add to persistent library
        definition.isLibraryDefinition(True)
        persistentLibrary.addPomsetContext(pomsetContext)
        
        # save out the bootstrap loader pomset
        # that will load this definition on the next startup
        persistentLibrary.saveBootstrapLoaderPomset()
        
        # update GUI
        self.emit(SIGNAL("OnPomsetMoved()"))

        return


    def OnDisplayDefinition(self, pomsetContext, 
                            definition=None, allowEdit=False):

        contextManager = self.app().contextManager()

        # import the modules
        import pomsets_app.gui.qt.edit_definition.widget as WidgetModule
        import pomsets_app.gui.qt.edit_definition.controller as ControllerModule

        # initialize the widget
        controller = ControllerModule.Controller(self)
        controller.shouldAllowEdit(allowEdit)
        controller.contextManager(contextManager)
        controller.pomsetContext(pomsetContext)
        controller.definition(definition)

        ui = WidgetModule.Ui_Dialog()
        ui.setupUi(controller)

        controller.widget(ui)

        # populate the dialog
        controller.populate()

        controller.show()

        return

    def OnEditParameterBinding(self, pomsetContext, definition, parameter):
        editTaskController = self.OnEditTask(pomsetContext, definition)
        controller = editTaskController.editParameterBinding(parameter)
        return controller

    def OnEditTask(self, pomsetContext, definition):
        """
        The task is actually the ReferenceDefinition
        from which the task will be built
        """

        contextManager = self.app().contextManager()

        # import the modules
        import pomsets_app.gui.qt.edit_task.widget as WidgetModule
        import pomsets_app.gui.qt.edit_task.controller as ControllerModule

        # initialize the widget
        controller = ControllerModule.Controller(self)
        controller.contextManager(contextManager)
        controller.pomsetContext(pomsetContext)
        controller.definition(definition)

        ui = WidgetModule.Ui_Dialog()
        ui.setupUi(controller)

        controller.widget(ui)

        # populate the dialog
        controller.populate()

        controller.show()

        return controller


    def OnDefinitionRemoved(self, library, pomsetContext):
        self.emit(SIGNAL("OnPomsetClosed(PyQt_PyObject)"), 
                  pomsetContext)
        return

    def OnCloudPoolConfiguration(self):

        contextManager = self.app().contextManager()

        # import the modules
        import pomsets_app.gui.qt.cloud_pool.widget as WidgetModule
        import pomsets_app.gui.qt.cloud_pool.controller as ControllerModule

        # initialize the widget
        controller = ControllerModule.Controller(self)
        controller.contextManager(contextManager)

        ui = WidgetModule.Ui_Dialog()
        ui.setupUi(controller)

        controller.widget(ui)

        # populate the dialog
        controller.populate()

        controller.show()

        return


    def OnEuca2oolsConfiguration(self):
        contextManager = self.app().contextManager()

        # import the modules
        import pomsets_app.gui.qt.euca2ools_configuration.widget as WidgetModule
        import pomsets_app.gui.qt.euca2ools_configuration.controller as ControllerModule

        # initialize the widget
        controller = ControllerModule.Controller(self)
        controller.contextManager(contextManager)

        ui = WidgetModule.Ui_Dialog()
        ui.setupUi(controller)

        controller.widget(ui)

        # populate the dialog
        controller.populate()

        controller.show()

        return


    def OnHadoopConfiguration(self):
        contextManager = self.app().contextManager()

        # import the modules
        import pomsets_app.gui.qt.hadoop_configuration.widget as WidgetModule
        import pomsets_app.gui.qt.hadoop_configuration.controller as ControllerModule

        # initialize the widget
        controller = ControllerModule.Controller(self)
        controller.contextManager(contextManager)

        ui = WidgetModule.Ui_Dialog()
        ui.setupUi(controller)

        controller.widget(ui)

        # populate the dialog
        controller.populate()

        controller.show()

        return


    def OnExecutePreview(self):
        contextManager = self.app().contextManager()

        # import the modules
        import pomsets_app.gui.qt.task_preview.widget as WidgetModule
        import pomsets_app.gui.qt.task_preview.controller as ControllerModule

        # initialize the widget
        controller = ControllerModule.Controller(self)
        controller.contextManager(contextManager)

        ui = WidgetModule.Ui_Dialog()
        ui.setupUi(controller)

        controller.widget(ui)

        # populate the dialog
        controller.populate()

        controller.show()

        return


    def OnExecuteLocal(self):
        self.OnExecutePomset(AutomatonModule.ID_EXECUTE_LOCAL)
        return
    

    def OnExecuteEucalyptus(self):
        self.OnExecutePomset(AutomatonModule.ID_EXECUTE_EUCA2OOLS)
        return


    def OnAboutApplication(self):
        # TODO:
        # should load from file?

        text = """
<body>
<strong>%s</strong> %s<br/>""" % (str(self.app().applicationVersion()),
                                  str(self.app().applicationName())) + \
        u"\u00A9 2010 michael j pan"+ \
        """<br/>
</body>
"""
        informativeText = """
<body>
<a href="http://pomsets.org">pomsets</a> is workflow management <br/>
for your cloud<br/>
<br/>
<a href="http://pomsets.org/License">License</a><br/>
</body>
"""
        msgBox = QtGui.QMessageBox(self)
        msgBox.setTextFormat(Qt.RichText)
        msgBox.setText(text)
        msgBox.setInformativeText(informativeText)
        msgBox.exec_()
        return
        

    def OnExitApplication(self):

        modifiedContexts = []

        contextManager = self.app().contextManager()


        mainSplitterWidget = self.centralWidget()
        librarySplitterWidget = mainSplitterWidget.widget(0)
        toolboxWidget = librarySplitterWidget.widget(1)
        transientLibraryWidget = toolboxWidget.widget(0)
        activeLibraryWidget = librarySplitterWidget.widget(0)

        for widget in [activeLibraryWidget, transientLibraryWidget]:
            definitionTable = widget.pomsetLibrary().definitionTable()
            filter = FilterModule.constructAndFilter()
            filter.addFilter(widget.pomsetFilter())
            filter.addFilter(RelationalModule.ColumnValueFilter(
                    'context',
                    FilterModule.ObjectKeyMatchesFilter(
                        FilterModule.IdentityFilter(True),
                        keyFunction = lambda x: x.isModified())))
            modifiedContexts.extend(
                RelationalModule.Table.reduceRetrieve(
                    definitionTable,
                    filter, ['context'], []))
            pass

        canExit = len(modifiedContexts) is 0

        if not canExit:
            msgBox = QtGui.QMessageBox(self)
            msgBox.setText("There are unsaved, modified pomsets.")
            msgBox.setInformativeText("Discard changes or cancel exit?")
            msgBox.setStandardButtons(
                QtGui.QMessageBox.Discard | 
                QtGui.QMessageBox.Cancel)
            msgBox.setDefaultButton(QtGui.QMessageBox.Cancel)
            ret = msgBox.exec_()
            if ret == QtGui.QMessageBox.Discard:
                canExit = True
            
        if canExit:
            sys.exit(0)

        return
    

    def OnExecutePomset(self, executionEnvId):

        contextManager = self.app().contextManager()

        try:
            import pomsets.command as ExecuteCommandModule
            commandBuilder = ExecuteCommandModule.CommandBuilder(
                ExecuteCommandModule.buildCommandFunction_commandlineArgs
            )
            commandBuilderMap = {
                'shell process':commandBuilder
            }

            # TODO:
            # is there a way to figure out env here,
            # rather than using executionEnvId
            
            requestKwds = contextManager.generateRequestKwds(
                executeEnvironmentId = executionEnvId,
                commandBuilderMap = commandBuilderMap)


            # TODO:
            # need to determine 

            contextManager.executePomset(
                pomset=contextManager.activePomset(), 
                requestKwds=requestKwds,
                shouldWait=False)

        except Exception, e:

            # TODO:
            # show an error box to the user
            messageBox = QtGui.QMessageBox(self)
            logging.error("Error executing pomset >> %s" % e)
            # messageBox.showMessage("Error executing pomset >> %s" % e)
            messageBox.setText('Execution error')
            messageBox.setInformativeText(str(e))
            messageBox.setIcon(QtGui.QMessageBox.Critical)
            messageBox.setStandardButtons(
                QtGui.QMessageBox.Ok)
            ret = messageBox.exec_()

            pass
        finally:
            # TODO:
            # update the execute menu items
            # i.e. disable execution for this pomset
            # now that execution has happened
            pass
            

        return


    # END class Frame
    pass
