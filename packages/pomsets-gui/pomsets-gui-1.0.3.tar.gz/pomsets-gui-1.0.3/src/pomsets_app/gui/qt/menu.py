from PyQt4 import QtGui
from PyQt4.QtCore import *
from PyQt4.QtOpenGL import *

import pypatterns.filter as FilterModule
import pypatterns.relational as RelationalModule

class ContextualMenu(QtGui.QMenu):

    def position(self, value=None):
        if value is not None:
            self._position = value
        if not hasattr(self, '_position'):
            self._position = None
        return self._position

    def selection(self, value=None):
        if value is not None:
            self._selection = value
        if not hasattr(self, '_selection'):
            self._selection = []
        return self._selection

    def contextManager(self, value=None):
        if value is not None:
            self._contextManager = value
        if not hasattr(self, '_contextManager'):
            self._contextManager = None
        return self._contextManager


    # END class ContextualMenu
    pass

class CanvasContextualMenu(ContextualMenu):

    def bindEvents(self):
        self.addAction(QString('Auto arrange'), self.OnAutoArrange)

        return

    def OnAutoArrange(self):
        canvas = self.contextManager().mainWindow().canvas
        canvas.computeLayout()
        canvas.updateGL()
        return


    # END class CanvasContextualMenu
    pass

class CanvasContextualMenuWithCreateNodeEnabled(CanvasContextualMenu):

    def bindEvents(self):
        contextManager = self.contextManager()
        pomsetContext, pomset = contextManager.currentDisplayedPomsetInfo()
        if not contextManager.hasTaskForPomset(pomsetContext.pomset()):
            self.addAction(QString('Create node'), self.OnCreateNode)
            self.addSeparator()

        CanvasContextualMenu.bindEvents(self)
        return

    def OnCreateNode(self):
        contextManager = self.contextManager()
        pomsetContext, pomset = contextManager.currentDisplayedPomsetInfo()

        # import the modules
        import pomsets_app.gui.qt.select_definition.widget as WidgetModule
        import pomsets_app.gui.qt.select_definition.controller as ControllerModule

        # initialize the widget
        controller = ControllerModule.Controller(self)
        controller.contextManager(contextManager)
        controller.pomsetContext(pomsetContext)
        controller.canvasPosition(self.position())

        ui = WidgetModule.Ui_Dialog()
        ui.setupUi(controller)

        controller.widget(ui)

        # populate the dialog
        controller.populate()

        controller.show()

        return

    # END class CanvasContextualMenuWithCreateNodeEnabled
    pass


class NodeContextualMenu(ContextualMenu):

    def bindEvents(self):

        contextManager = self.contextManager()

        pomsetContext, pomset = contextManager.currentDisplayedPomsetInfo()
        if not contextManager.hasTaskForPomset(pomsetContext.pomset()):
 
            self.addAction(QString('Edit task'), self.OnEditTask)

            # should also add "Edit definition"
            # if the definition is not a library definition
            dataNode = self.selection()[0].nodeData
            if not dataNode.definitionToReference().isLibraryDefinition():
                self.addAction(QString('Edit definition'), 
                               self.OnEditTaskDefinition)
            else:
                self.addAction(QString('View definition'), 
                               self.OnViewTaskDefinition)

            self.addAction(QString('Duplicate'), self.OnDuplicate)
            self.addAction(QString('Delete'), self.OnDelete)
        else:
            # enabled only if the node has executed or errored out
            # and there's only one node selected
            if len(self.selection()) == 1:
                self.addAction(QString('View output messages'), 
                               self.OnViewOutputMessages)

        return


    def OnEditTask(self):

        contextManager = self.contextManager()

        guiNode = self.selection()[0]
        definitionToEdit = guiNode.nodeData

        pomsetContext, pomset = contextManager.currentDisplayedPomsetInfo()

        self.contextManager().mainWindow().OnEditTask(
            pomsetContext, definitionToEdit)

        return

    
    def OnViewTaskDefinition(self):
        self.OnDisplayTaskDefinition(False)
    
    def OnEditTaskDefinition(self):
        self.OnDisplayTaskDefinition(True)

    def OnDisplayTaskDefinition(self, allowEdit):

        contextManager = self.contextManager()

        guiNode = self.selection()[0]
        dataNode = guiNode.nodeData
        definitionToEdit = dataNode.definitionToReference()

        # now determine if the definition is in the transient library
        # or defined internally in the pomset
        # and then get the pomset context associated with that definition
        filter = RelationalModule.ColumnValueFilter(
            'definition',
            FilterModule.IdentityFilter(definitionToEdit))
        library = contextManager.transientLibrary()
        if library.hasDefinition(filter):
            contexts = RelationalModule.Table.reduceRetrieve(
                library.definitionTable(), filter, ['context'], [])
            pomsetContext = contexts[0]
            pass
        else:
            pomsetContext, pomset = contextManager.currentDisplayedPomsetInfo()

        self.contextManager().mainWindow().OnDisplayDefinition(
            pomsetContext, definitionToEdit, allowEdit=allowEdit)
        return


    def OnDelete(self):
        contextManager = self.contextManager()
        contextManager.mainWindow().OnDeleteNodes(self.selection())
        return

    def OnDuplicate(self):
        contextManager = self.contextManager()
        contextManager.mainWindow().OnDuplicateNodes(self.selection())
        return

    def OnViewOutputMessages(self):

        contextManager = self.contextManager()
        pomsetContext, pomset = contextManager.currentDisplayedPomsetInfo()

        # import the modules
        import pomsets_app.gui.qt.task_output.widget as WidgetModule
        import pomsets_app.gui.qt.task_output.controller as ControllerModule

        # initialize the widget
        controller = ControllerModule.Controller(self)
        controller.contextManager(contextManager)
        controller.pomsetContext(pomsetContext)

        ui = WidgetModule.Ui_Dialog()
        ui.setupUi(controller)

        controller.widget(ui)

        # populate the dialog
        controller.populate()

        controller.show()


        return

    # END class NodeContextualMenu
    pass


class EdgeContextualMenu(ContextualMenu):

    def bindEvents(self):
        self.addAction(QString('Disconnect edge'), self.OnDisconnect)
        return

    def OnDisconnect(self):

        contextManager = self.contextManager()
        builder = contextManager.pomsetBuilder()

        edge = self.selection()[0]

        pomsetContext, pomset = contextManager.currentDisplayedPomsetInfo()
        
        builder.disconnect(pomset,
                           edge.inputNode().nodeData,
                           edge.inputPort().name,
                           edge.outputNode().nodeData,
                           edge.outputPort().name)
                           
        contextManager.mainWindow().emit(
            SIGNAL("OnPomsetModified(PyQt_PyObject)"), pomsetContext)


        return

    # END class EdgeContextualMenu
    pass


class PortContextualMenu(ContextualMenu):

    def bindEvents(self):
        self.addAction(QString('Edit value'), self.OnEditValue)
        return

    def OnEditValue(self):

        selected = self.selection()[0]

        contextManager = self.contextManager()
        pomsetContext, pomset = contextManager.currentDisplayedPomsetInfo()

        dataNode = selected.node.nodeData
        parameterId = selected.name
        parameter = dataNode.getParameter(parameterId)

        import pomsets.parameter as ParameterModule

        if parameter.portType() == ParameterModule.PORT_TYPE_DATA:
            contextManager.mainWindow().OnEditParameterBinding(
                pomsetContext, dataNode, parameter)
        return

    # END class PortContextualMenu
    pass


class ActivePomsetContextualMenu(ContextualMenu):

    def bindEvents(self):
        self.addAction(QString('New'), self.OnCreate)

        self.addAction(QString('Load'), self.OnLoad)

        pomsetContext, pomset = self.selection()
        if pomsetContext is not None:
            
            # need a "save" and "save as"
            if pomsetContext.url() is not None:
                self.addAction(QString('Save'), self.OnSave)

            self.addAction(QString('Save as'), self.OnSaveAs)

            self.addAction(QString('Close'), self.OnClose)

            pass


        return

    def OnCreate(self):
        self.contextManager().mainWindow().OnCreateNewTopLevelPomset()
        return

    def OnLoad(self):
        self.contextManager().mainWindow().OnLoadTopLevelPomset()
        return

    def OnSave(self):
        context = self.selection()[0]
        self.contextManager().mainWindow().OnSavePomset(
            context, context.url())
        return

    def OnSaveAs(self):
        context = self.selection()[0]
        self.contextManager().mainWindow().OnSavePomset(context)
        return

    def OnClose(self):
        contextManager = self.contextManager()
        contextManager.mainWindow().OnCloseActivePomset(self.selection()[0])

        return

    # END class ActivePomsetContextualMenu
    pass


class LibraryDefinitionContextualMenu(ContextualMenu):
    
    def bindEvents(self):

        pomsetContext, pomset = self.selection()
        if pomsetContext is not None:
            # add the "Delete menu item
            self.addAction('Remove', self.OnRemoveDefinition)

        return

    def OnRemoveDefinition(self):

        pomsetContext, pomset = self.selection()
        contextManager = self.contextManager()


        persistentLibrary = contextManager.persistentLibrary()
        
        # backup the existing library
        UtilsModule.backupLibrary(
            persistentLibrary.bootstrapLoaderDefinitionsDir())
        
        definitionFilter = RelationalModule.ColumnValueFilter(
            'definition',
            FilterModule.IdentityFilter(pomset)
        )
        
        # remove from transient library
        persistentLibrary.removeDefinition(definitionFilter)
        
        # remove the definition from the file system
        definitionUrl = os.path.sep.join([
                persistentLibrary.bootstrapLoaderDefinitionsDir(),
                pomset.url()])

        if not os.path.exists(definitionUrl):
            logging.error('cannot remove definition from url %s' % definitionUrl)
            return
        else:
            os.unlink(definitionUrl)
            
        # save out the new bootstrapper pomset
        # that will not load the just removed pomset
        persistentLibrary.saveBootstrapLoaderPomset()

        contextManager.mainWindow().OnDefinitionRemoved(
            persistentLibrary, pomsetContext)

        return


    # END class LibraryDefinitionContextualMenu
    pass



class LoadedDefinitionContextualMenu(ContextualMenu):


    def bindEvents(self):
        self.addAction(QString('New'), self.OnCreateDefinition)

        pomsetContext, pomset = self.selection()

        if pomsetContext is not None:
            # add the "Edit" menu item
            # add the "Delete menu item
            self.addAction(QString('Edit'), self.OnEditDefinition)
            self.addAction(QString('Remove'), self.OnRemoveDefinition)

            self.addSeparator()
            self.addAction(QString('Add to library'), self.OnAddDefinitionToLibrary)
            
            # TODO:
            # need a "save" and "save as"
            self.addAction(QString('Save'), self.OnSave)
            self.addAction(QString('Save as'), self.OnSaveAs)
            pass

        self.addSeparator()
        self.addAction(QString('Load from file'), self.OnLoadFromFile)

        return

    def OnCreateDefinition(self):
        self.contextManager().mainWindow().OnCreateNewAtomicPomset()
        return


    def OnEditDefinition(self):
        pomsetContext, pomset = self.selection()
        self.contextManager().mainWindow().OnDisplayDefinition(
            pomsetContext, definition=pomset, allowEdit=True)
        return


    def OnRemoveDefinition(self):

        pomsetContext, pomset = self.selection()
        contextManager = self.contextManager()
        transientLibrary = contextManager.transientLibrary()


        # remove from transient library
        definitionFilter = RelationalModule.ColumnValueFilter(
            'definition',
            FilterModule.IdentityFilter(pomset)
        )
        transientLibrary.removeDefinition(definitionFilter)

        contextManager.mainWindow().OnDefinitionRemoved(
            transientLibrary, pomsetContext)
        return


    def OnAddDefinitionToLibrary(self):
        context = self.selection()[0]
        self.contextManager().mainWindow().OnMoveDefinitionToLibrary(context)
        return

    def OnSave(self):
        context = self.selection()[0]
        self.contextManager().mainWindow().OnSavePomset(
            context, context.url())
        return

    def OnSaveAs(self):
        context = self.selection()[0]
        self.contextManager().mainWindow().OnSavePomset(context)
        return

    def OnLoadFromFile(self):
        contextManager = self.contextManager()
        transientLibrary = contextManager.transientLibrary()

        filter = FilterModule.ObjectKeyMatchesFilter(
            filter = FilterModule.IdentityFilter(True),
            keyFunction = lambda x: x.pomset().isAtomic()
            )
        contextManager.mainWindow().OnLoadPomsetIntoLibrary(
            transientLibrary, filter=filter)
        return

    # END class LoadedDefinitionContextualMenu
    pass
