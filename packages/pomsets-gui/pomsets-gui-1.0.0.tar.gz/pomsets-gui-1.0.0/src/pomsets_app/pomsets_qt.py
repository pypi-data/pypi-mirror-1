import logging
import os
import platform
import shutil
import sys
import unittest
import user

import pypatterns.command as CommandPatternModule

import zgl_graphdrawer
import zgl_graphdrawer.application as ApplicationModule
import zgl_graphdrawer.utils as UtilsModule

import cloudpool as CloudModule
import cloudpool.shell as ShellModule

import pomsets_app.controller.automaton as AutomatonModule
import pomsets_app.controller.context as ContextModule
import pomsets_app.gui.graph as GraphModule
import pomsets_app.gui.policy as PolicyModule
import pomsets_app.utils as AppUtilsModule

import pomsets_app.gui.qt.frame as FrameModule


from PyQt4 import QtGui
from PyQt4.QtCore import *


def getDefaultResourcePath():

    # TODO:
    # need to figure out how to determine the application's
    # resource path on different platforms

    endIndex = __file__.rfind('src')
    if endIndex == -1:
        # this is production (not development mode)
        endIndex = __file__.rfind('pomsets-gui')

    appRoot = __file__[:endIndex]
    if appRoot.endswith(os.path.sep):
        appRoot = appRoot[:-1]

    if platform.system() in ['Darwin']:

        """
        QtGui.QApplication.applicationFilePath()
        /Users/mjpan/pomsets/pomsets.20100227/pomsets-gui/dist/pomsets-gui.app/Contents/MacOS/pomsets-gui
        """

        hasDeterminedResourcePath = False

        applicationFilePath = str(QtGui.QApplication.applicationFilePath())

        pathToTest = 'pomsets-gui.app/Contents/MacOS' 
        if pathToTest in applicationFilePath:
            # we're using the application bundle
            resourcePath = applicationFilePath[:applicationFilePath.index(pathToTest)+len(pathToTest)-len('MacOS')] + 'Resources'
            hasDeterminedResourcePath = True
            pass
            
        pathToTest = 'pomsets.app/Contents/MacOS'
        if not hasDeterminedResourcePath and pathToTest in applicationFilePath:
            # we're using the application bundle
            resourcePath = applicationFilePath[:applicationFilePath.index(pathToTest)+len(pathToTest)-len('MacOS')] + 'Resources'
            hasDeterminedResourcePath = True
            pass

        if not hasDeterminedResourcePath:
            # we're not in the bundle, so a dev env,
            # use the dev default
            resourcePath = os.path.join(os.getcwd(), appRoot, 'resources')

        pass
    else:
        resourcePath = os.path.join(os.getcwd(), appRoot, 'resources')


    return resourcePath



class Application(ApplicationModule.Application, QtGui.QApplication):

    def __init__(self, name):
        QtGui.QApplication.__init__(self, name)
        ApplicationModule.Application.__init__(self)
        return

    def initializeResources(self):
        resourcePath = getDefaultResourcePath()
        self.setResourcePath(resourcePath)

        return
        
    def initializePolicies(self):

        self.setResourceValue('node policy class',
                             PolicyModule.NodePolicy)
        self.setResourceValue('visual policy class',
                             PolicyModule.VisualPolicy)

        config = AppUtilsModule.loadConfig()

        layoutClass = PolicyModule.BasicLayoutPolicy
        """
        try:
            import gv

            # TODO:
            # need to spcify the Python API version
            print "imported gv"
            layoutClass = PolicyModule.LayoutPolicyModule.GraphVizLayoutPolicy
        except ImportError:
            graphvizConfigurations = config.get('graphviz configurations', [])
            if len(graphvizConfigurations):
                graphvizConfiguration = graphvizConfigurations[0]
                dotCommandPath = graphvizConfiguration.get('dot command path')
                if dotCommandPath and os.path.exists(dotCommandPath):
                    print "found graphviz configuration"
                    layoutClass = PolicyModule.LayoutPolicyModule.GraphVizLayoutPolicy
                pass
            pass
        """
        graphvizConfigurations = config.get('graphviz configurations', [])
        if len(graphvizConfigurations):
            graphvizConfiguration = graphvizConfigurations[0]
            dotCommandPath = graphvizConfiguration.get('dot command path')
            if dotCommandPath and os.path.exists(dotCommandPath):
                layoutClass = PolicyModule.LayoutPolicyModule.GraphVizLayoutPolicy
                try:
                    import gv
                    # import succeeded
                    # so we can use gv_python to generate 
                    # the dot file with the non-positioned nodes
                    layoutClass = PolicyModule.GraphvizLayoutPolicy
                except ImportError:
                    # gv_python not installed
                    # use default one where we generate the dot file
                    pass
            pass

        self.setResourceValue('layout policy class', layoutClass)


        ApplicationModule.Application.initializePolicies(self)

        return

    def initializeFonts(self):

        # TODO:
        # this was copied from, and should use
        # the visual policy function instead
        fontsDir = os.sep.join([self.contextManager().resourcePath(),
                                'fonts'])
        fontPath = os.sep.join([fontsDir, 'FreeUniversal-Regular.ttf'])
        fontId = QtGui.QFontDatabase.addApplicationFont(fontPath)
        if fontId is not -1:
            self._defaultFontId = fontId
            fontFamilies = QtGui.QFontDatabase.applicationFontFamilies(fontId)
            # returns 'FreeUniversal'
        self._fontDb = QtGui.QFontDatabase()
        fontStyles = self._fontDb.styles('FreeUniversal')
        return

    # END class Application
    pass



def initializeResources(app):


    # need to ensure that the config file exists
    configPath = AppUtilsModule.getDefaultConfigPath()
    if not os.path.exists(configPath):
        configDir = os.path.dirname(configPath)
        if not os.path.exists(configDir):
            os.makedirs(configDir)
        initializeAppConfig(resourcePath)

    config = AppUtilsModule.loadConfig()

    if not 'application settings' in config:
        initializeAppSettings(config)

    applicationSettings = config['application settings']

    import pomsets_app.gui.qt.menu as MenuModule
    if applicationSettings.get('create node via canvas contextual menu', False):
        app.setResourceValue('canvas contextual menu class',
                             MenuModule.CanvasContextualMenuWithCreateNodeEnabled)
    else:
        app.setResourceValue('canvas contextual menu class',
                             MenuModule.CanvasContextualMenu)

    app.setResourceValue('canvas contextual menu class',
                         MenuModule.CanvasContextualMenuWithCreateNodeEnabled)


    app.setResourceValue('gui node class',
                         GraphModule.Node)
    app.setResourceValue('gui nest node class',
                         GraphModule.NestNode)
    app.setResourceValue('gui loop node class',
                         GraphModule.LoopNode)
    app.setResourceValue('gui branch node class',
                         GraphModule.BranchNode)
    app.setResourceValue('gui edge class',
                         GraphModule.Edge)
    app.setResourceValue('gui port class',
                         GraphModule.Port)
    return


def createApplicationFrame(app):
    frame = FrameModule.Frame()
    frame.app(app)
    app.contextManager().mainWindow(frame)
    frame.initializeWidgets()
    frame.setWidgetDataSources()
    frame.populateWidgets()
    return frame


def createApplicationContext(app):
    contextManager = initializeContextManager()
    app.contextManager(contextManager)
    contextManager.app(app)

    # set the location of the resources for this application
    if not hasattr(app, '_resourcePath'):
        raise AttributeError('need to have set the resource path')
    app.contextManager().resourcePath(app._resourcePath)

    contextManager.initializeLibraries()

    automaton = initializeAutomaton(app)

    # startup the thread
    automaton.startProcessEndedTasksThread()

    import pomsets.library as LibraryModule

    library = contextManager.persistentLibrary()
    definition = library.getBootstrapLoader()
    executeEnvironment = LibraryModule.LibraryLoader(library)
    commandBuilder = LibraryModule.CommandBuilder()
    commandBuilderMap = {
        'library bootstrap loader':commandBuilder,
        'python eval':commandBuilder
    }

    requestKwds = contextManager.generateRequestKwds(
        executeEnvironment=executeEnvironment,
        executeEnvironmentId = AutomatonModule.ID_EXECUTE_LOCAL,
        commandBuilderMap=commandBuilderMap)
    
    compositeTask = contextManager.executePomset(
        pomset=definition,
        requestKwds=requestKwds)

    # handle the case where there are errors on loading
    childTasks = compositeTask.getChildTasks()
    failedChildTasks = [x for x in childTasks if 
                        x.workRequest().exception]
    if len(failedChildTasks):
        #raise NotImplementedError(
        #    'should query user to remove from library')
        logging.error('should query user to remove from library')
        
    return

def initializeCanvas(app, frame):

    # frame = app.GetTopWindow()
    canvas = frame.canvas
    contextManager = app.contextManager()

    contextManager.initializeCanvas(canvas=canvas)
    contextManager.initializeEventHandlers()

    app.initializePolicies()
    app.initializeFonts()

    return

def createInitialPomsetContext(app):
    contextManager = app.contextManager()

    newPomsetContext = contextManager.createNewPomset(name="new pomset")
    newPomsetContext.isModified(False)
    contextManager.addActivePomsetContext(newPomsetContext)

    return newPomsetContext


def initializeContextManager():
    contextManager = ContextModule.QtContextManager()        

    return contextManager


def initializeAppSettings(config):

    if not 'application settings' in config:
        config['application settings'] = {}

    applicationSettings = config['application settings']

    # we need to make this distinction between how nodes are created
    # because linux does not seem to handle end drag events
    # and because macs typically don't have right mouse buttons
    if platform.system() in ['Darwin']:
        applicationSettings['create node via dnd'] = True
        applicationSettings['create node via canvas contextual menu'] = False
        pass
    elif platform.system() in ['Linux']:
        applicationSettings['create node via dnd'] = False
        applicationSettings['create node via canvas contextual menu'] = True
        pass
    return

def initializeAppConfig(resourcePath):

    configPath = AppUtilsModule.getDefaultConfigPath()

    # first, copy the config file
    shutil.copyfile(os.path.join(resourcePath, 'config', 'config'),
                    configPath)

    # now add the platform specific stuff
    config = AppUtilsModule.loadConfig()
    initializeAppSettings(config)

    AppUtilsModule.saveConfig(config, configPath=configPath)
    return


def initializeAutomaton(app):

    automaton = AutomatonModule.Automaton()

    contextManager = app.contextManager()
    contextManager.initializeAutomaton(automaton)

    config = AppUtilsModule.loadConfig()
    automaton.loadConfig(config)


    # determine if graphviz is specified
    dotCommandPath = ''
    graphvizConfigurations = automaton.otherConfigurations().get('graphviz configurations')
    if graphvizConfigurations and len(graphvizConfigurations):
        graphvizConfiguration = graphvizConfigurations[0]
        dotCommandPath = graphvizConfiguration.get('dot command path', '')
        pass
    contextManager.commandPath('dot', dotCommandPath)
    logging.debug('using %s as the dot command path' % dotCommandPath)


    # initialize the threadpool
    # this is for testing vm execution
    # should start with 0

    # this is for local execution
    threadpool = CloudModule.Pool(0)
    automaton.setThreadPool(AutomatonModule.ID_EXECUTE_LOCAL, threadpool)
    worker = threadpool.assignWorker()
    shell = ShellModule.LocalShell()
    worker.executeEnvironment(shell)

    # this is for remote execution
    credentials = automaton.remoteExecuteCredentials()
    if len(credentials):
        threadpool = CloudModule.Pool(0)
        automaton.setThreadPool(AutomatonModule.ID_EXECUTE_REMOTE, threadpool)

        credential = credentials[0]
        # TODO:
        # should wait until the user
        hostname = credential['hostname']
        userLogin = credential['user']
        keyfile = credential['keyfile']
        worker = threadpool.assignWorker()
        shell = ShellModule.SecureShell()
        shell.hostname(hostname)
        shell.user(userLogin)
        shell.keyfile(keyfile)
        worker.executeEnvironment(shell)

    """
    credentialEntries = [
        x for x in automaton.getCloudControllerCredentials(
            columns=AutomatonModule.Automaton.COLUMNS_CLOUDCONTROLLERCREDENTIALS)
    ]
    if len(credentialEntries):
        for credentialEntry in credentialEntries:
            credentials = credentialEntry[2]
            api = credentialEntry[1]
            name = credentialEntry[0]
            if api == 'euca2ools':
                # this is for cloud execution
                threadpool = CloudModule.Pool(0)
                automaton.setThreadPool(AutomatonModule.ID_EXECUTE_EUCA2OOLS, threadpool)
                # threadpool.credentials(credentials)
            else:
                logging.warn('not implemented for %s API' % api)


            # serviceName
            # serviceAPI
            # values
            pass
        pass
    """
    threadpool = CloudModule.Pool(0)
    automaton.setThreadPool(AutomatonModule.ID_EXECUTE_EUCA2OOLS, threadpool)


    # start the thread 
    automaton.startProcessEndedTasksThread()

    automaton.commandManager(CommandPatternModule.CommandManager())



    return automaton


def showSplashScreen():

    resourcePath = getDefaultResourcePath()
    # splashImage = os.path.join(resourcePath, 'images', 'logo.png')

    pixmap = QtGui.QPixmap(splashImage)
    splash = QtGui.QSplashScreen(pixmap)
    splash.show()

    # if mac, will need to call raise
    splash.raise_()
    return


def main():


    # app = ApplicationModule.wxApplication()
    app = Application(['pomsets'])
    app.setApplicationName('pomsets')
    app.setApplicationVersion('1.0.0')

    # showSplashScreen()

    initializeResources(app)
    app.initializeResources()


    createApplicationContext(app)

    frame = createApplicationFrame(app)

    initializeCanvas(app, frame)


    newPomsetContext = createInitialPomsetContext(app)
    frame.displayPomset(newPomsetContext)
    frame.emit(SIGNAL("OnPomsetLoaded(PyQt_PyObject)"), newPomsetContext)




    # frame = app.GetTopWindow()
    # frame.Show()
    # app.MainLoop()
    frame.show()
    app.exec_()

    # teardown, now that control of the event loop
    # has been returned to us
    automaton = app.contextManager().automaton()
    automaton.shouldProcessEndedTasks(False)

    return

if __name__=="__main__":
    main()

