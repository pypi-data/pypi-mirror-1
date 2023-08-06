import os

import pomsets_app.controller.automaton as AutomatonModule


class Frame(object):

    def app(self, value=None):
        if value is not None:
            self._app = value
        return self._app

    def displayPomset(self, pomsetContext, pomset=None):
        
        canvas = self.canvas

        contextManager = self.app().contextManager()

        if pomsetContext is None:
            contextManager.currentDisplayedPomsetInfo((None, None))
            canvas.breadCrumbs('No active pomset to display')
            canvas.OnRefresh()
            return

        # after this point
        # it is assumed that pomsetContext is not None

        if pomset is None:
            pomset = pomsetContext.pomset()
        
        contextManager.currentDisplayedPomsetInfo((pomsetContext, pomset))

        # display the actual pomset in the canvas
        canvas.displayPomset(pomset)

        if contextManager.hasTaskForPomset(pomsetContext.pomset()):
            # TODO:
            # need to handle the case where
            # we are displaying a deeply nested pomset
            rootTask = contextManager.getTaskForPomset(pomsetContext.pomset())
            canvas.updateExecutionStatus(rootTask)

        self.setBreadCrumbs(pomsetContext, pomset)
        
        return


    def updatePomsetMenu(self):
        contextManager = self.app().contextManager()
        activePomsetContext = contextManager.activePomsetContext()
        #self.setMenuItemActive(
        #    'Pomset', 'Close', activePomsetContext is not None)

        return
    
    def updateExecuteMenus(self):

        contextManager = self.app().contextManager()
        pomsetContext, pomset = contextManager.currentDisplayedPomsetInfo()

        # update the menus
        shouldEnableExecute = True
        if contextManager.hasTaskForPomset(pomsetContext.pomset()):
            # disable the execute menu
            shouldEnableExecute = False
            pass

        try:
            threadPoolId = AutomatonModule.ID_EXECUTE_EUCA2OOLS
            threadPool = contextManager.automaton().getThreadPoolUsingId(
                threadPoolId)
            shouldEnableExecuteEuca2ools = shouldEnableExecute
            if threadPool.isEmpty():
                # disable the execute eucalyptus menu item
                shouldEnableExecuteEuca2ools = False
                pass
        except ValueError, e:
            # this is probably because the threadpool
            # for euca2ools was not created
            shouldEnableExecuteEuca2ools = False
            pass

        #self.setMenuItemActive('Execute', 'Local', shouldEnableExecute)
        #self.setMenuItemActive('Execute', 'Euca2ools', shouldEnableExecuteEuca2ools)

        return

    def selectActivePomset(self, pomset):
        
        # currently a placeholder
        # need to figure out the pomset currently being displayed
        # and select that in the GUI
        if self._updateActivePomsetTreeCtrlSelection:
            print "should update selection"

        
        # set the breadcrumbs for the pomset to be displayed
        contextManager = self.app().contextManager()
        activeContext = contextManager.activePomsetContext()

        return


    def setBreadCrumbs(self, pomsetContext, pomset):
        contextPath = pomsetContext.getContextPathFor(pomset)

        canvas = self.canvas
        canvas.breadCrumbs(' > '.join([x.name() for x in contextPath]))
        
        return

    # END class Frame
    pass


