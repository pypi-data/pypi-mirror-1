import logging
import os

from PyQt4.QtCore import *
from PyQt4 import QtGui

import pypatterns.filter as FilterModule

import pomsets.parameter as ParameterModule
import pomsets.task as TaskModule

import pomsets_app.utils as AppUtilsModule
import pomsets_app.gui.qt as QtModule

class Controller(QtModule.Controller, QtGui.QDialog):


    def __init__(self, *args, **kwds):
        QtGui.QDialog.__init__(self, *args, **kwds)
        QtModule.Controller.__init__(self)

        return

    def populate(self):

        widget = self.widget()
        contextManager = self.contextManager()

        splitter = widget.splitter

        treeTasks = widget.treeTasks
        
        pomsetContext = self.pomsetContext()
        pomset = pomsetContext.pomset()
        task = contextManager.getTaskForPomset(pomset)

        # populate the tree
        treeTasks.setHeaderLabels(['Tasks'])
        item = QtGui.QTreeWidgetItem([pomset.name()])
        item.setData(0, Qt.UserRole, task)
        treeTasks.addTopLevelItem(item)
        self.addChildTasks(task, item)
        
        treeTasks.expandAll()

        handle = splitter.handle(0)

        return


    def addChildTasks(self, task, parentItem):
        widget = self.widget()
        contextManager = self.contextManager()
        treeTasks = widget.treeTasks

        
        for index, childTask in enumerate(task.getChildTasks()):
            name = task.definition().name()
            item = QtGui.QTreeWidgetItem([name])
            item.setData(0, Qt.UserRole, childTask)
            parentItem.addChild(item)
            if isinstance(childTask, TaskModule.CompositeTask):
                self.addChildTasks(childTask, item)
            pass

        return


    @pyqtSlot(QtGui.QTreeWidgetItem, int)
    def on_treeTasks_itemClicked(self, item, int):

        task = item.data(0, Qt.UserRole).toPyObject()

        request = task.workRequest()
        stream = request.kwds.get('process message output', None)

        lines = []

        executedCommand = request.kwds.get('executed command', None)
        if executedCommand:
            lines.append('# executed command\n')
            lines.append('# %s \n' % ' '.join(executedCommand))
            lines.append('\n')

        if stream is not None:
            lines.extend(stream.readlines())

        if request.kwds.get('exception stack trace', None) is not None:
            exceptionStackTrace = request.kwds.get('exception stack trace')
            lines.extend(exceptionStackTrace)

        value = ''.join(lines)

        widget = self.widget()
        textEditOutput = widget.textEditOutput
        textEditOutput.setText(value)


        return




    # END class Controller
    pass
