import logging
import os
import platform
import shutil

from PyQt4 import QtGui
from PyQt4.QtCore import *

import pypatterns.command as CommandPatternModule

import cloudpool as CloudModule
import cloudpool.shell as ShellModule


import zgl_graphdrawer.application as ApplicationModule

import pomsets.library as LibraryModule


import pomsets_app.utils as AppUtilsModule
import pomsets_app.controller.automaton as AutomatonModule
import pomsets_app.controller.context as ContextModule

import pomsets_app.gui.graph as GraphModule

import pomsets_app.gui.qt.frame as FrameModule
import pomsets_app.gui.qt.menu as MenuModule
import pomsets_app.gui.policy as PolicyModule




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

    def __init__(self):
        QtGui.QApplication.__init__(self, [])
        ApplicationModule.Application.__init__(self)

        self.setApplicationName('pomsets')
        self.setApplicationVersion('1.0.2')

        return


    def runProgram(self):
        resourcePath = getDefaultResourcePath()
        self.setResourcePath(resourcePath)

        self.createApplicationContext()
        self.createApplicationFrame()

        if self.shouldQueryUserForLicenseAgreement():
            self.showLicenseFrame()
            self.exec_()

        if self.userHasAgreedToLicense():
            self.initializeForMainProgram()
            self.showMainFrame()
            self.exec_()

            # teardown, now that control of the event loop
            # has been returned to us
            automaton = self.contextManager().automaton()
            automaton.shouldProcessEndedTasks(False)
            return

        return



    def showSplashScreen(self):

        resourcePath = getDefaultResourcePath()
        # splashImage = os.path.join(resourcePath, 'images', 'logo.png')

        pixmap = QtGui.QPixmap(splashImage)
        splash = QtGui.QSplashScreen(pixmap)
        splash.show()

        # if mac, will need to call raise
        splash.raise_()
        return



    def showLicenseFrame(self):
        frame = self.getLicenseFrame(self.contextManager().mainWindow())
        frame.show()
        return

    def showMainFrame(self):
        self.contextManager().mainWindow().show()
        return

    def shouldQueryUserForLicenseAgreement(self):
        if self.userHasAgreedToLicense():
            return False
        return True

    def getLicenseFile(self):
        configDir = AppUtilsModule.getDefaultConfigDir()
        licenseFile = os.path.join(configDir, '.license')
        return licenseFile

    def userHasAgreedToLicense(self):
        licenseFile = self.getLicenseFile()
        return os.path.exists(licenseFile)


    def getLicenseFrame(self, parentWindow):
        contextManager = self.contextManager()

        # import the modules
        import pomsets_app.gui.qt.license_agreement.widget as WidgetModule
        import pomsets_app.gui.qt.license_agreement.controller as ControllerModule

        # initialize the widget
        controller = ControllerModule.Controller(parentWindow)
        controller.contextManager(contextManager)

        ui = WidgetModule.Ui_Dialog()
        ui.setupUi(controller)

        controller.widget(ui)

        # populate the dialog
        controller.populate()

        return controller



    def initializeForMainProgram(self):
        
        self.contextManager().initializeLibraries()
        self.initializeResources()
        self.initializeAutomaton()
        self.initializeFrame()
        self.createInitialPomsetContext()
        return



    def initializeResources(self):


        # need to ensure that the config file exists
        configPath = AppUtilsModule.getDefaultConfigPath()
        if not os.path.exists(configPath):
            configDir = os.path.dirname(configPath)
            if not os.path.exists(configDir):
                os.makedirs(configDir)
            resourcePath = getDefaultResourcePath()
            initializeAppConfig(resourcePath)

        config = AppUtilsModule.loadConfig()

        if not 'application settings' in config:
            initializeAppSettings(config)

        applicationSettings = config['application settings']

        if applicationSettings.get('create node via canvas contextual menu', False):
            self.setResourceValue('canvas contextual menu class',
                                 MenuModule.CanvasContextualMenuWithCreateNodeEnabled)
        else:
            self.setResourceValue('canvas contextual menu class',
                                 MenuModule.CanvasContextualMenu)

        self.setResourceValue('canvas contextual menu class',
                             MenuModule.CanvasContextualMenuWithCreateNodeEnabled)


        self.setResourceValue('gui node class',
                             GraphModule.Node)
        self.setResourceValue('gui nest node class',
                             GraphModule.NestNode)
        self.setResourceValue('gui loop node class',
                             GraphModule.LoopNode)
        self.setResourceValue('gui branch node class',
                             GraphModule.BranchNode)
        self.setResourceValue('gui edge class',
                             GraphModule.Edge)
        self.setResourceValue('gui port class',
                             GraphModule.Port)


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


    def createApplicationFrame(self):
        frame = FrameModule.Frame()
        frame.app(self)
        self.contextManager().mainWindow(frame)
        return frame

    def initializeFrame(self):
        frame = self.contextManager().mainWindow()
        frame.initializeWidgets()
        frame.setWidgetDataSources()
        frame.populateWidgets()

        self.initializeCanvas(frame)
        return


    def initializeCanvas(self, frame):

        canvas = frame.canvas
        contextManager = self.contextManager()

        contextManager.initializeCanvas(canvas=canvas)
        contextManager.initializeEventHandlers()

        self.initializePolicies()
        self.initializeFonts()

        return


    def createInitialPomsetContext(self):
        contextManager = self.contextManager()

        newPomsetContext = contextManager.createNewPomset(name="new pomset")
        newPomsetContext.isModified(False)
        contextManager.addActivePomsetContext(newPomsetContext)

        frame = contextManager.mainWindow()
        frame.displayPomset(newPomsetContext)
        frame.emit(SIGNAL("OnPomsetLoaded(PyQt_PyObject)"), newPomsetContext)

        return newPomsetContext




    def createApplicationContext(self):
        contextManager = ContextModule.QtContextManager()        

        self.contextManager(contextManager)
        contextManager.app(self)

        # set the location of the resources for this application
        if not hasattr(self, '_resourcePath'):
            raise AttributeError('need to have set the resource path')
        self.contextManager().resourcePath(self._resourcePath)


        return


    def initializeAutomaton(self):

        automaton = AutomatonModule.Automaton()

        contextManager = self.contextManager()

        contextManager.initializeAutomaton(automaton)

        config = AppUtilsModule.loadConfig()
        automaton.loadConfig(config)


        # determine if graphviz is specified
        dotCommandPath = ''
        graphvizConfigurations = automaton.otherConfigurations().get(
            'graphviz configurations')
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


        automaton.commandManager(CommandPatternModule.CommandManager())

        # startup the thread
        automaton.startProcessEndedTasksThread()


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

        return automaton



    # END class Application
    pass
