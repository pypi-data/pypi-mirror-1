import os
import uuid

from PyQt4.QtCore import *
from PyQt4 import QtGui

import pypatterns.filter as FilterModule
import pypatterns.relational as RelationalModule

import pomsets.parameter as ParameterModule

import pomsets_app.gui.qt as QtModule

class Controller(QtModule.Controller, QtGui.QDialog):

    def __init__(self, *args, **kwds):
        QtGui.QDialog.__init__(self, *args, **kwds)
        QtModule.Controller.__init__(self)
        return

    def shouldAllowEdit(self, value=None):
        if value is not None:
            self._shouldAllowEdit = value
        if not hasattr(self, '_shouldAllowEdit'):
            self._shouldAllowEdit = False
        return self._shouldAllowEdit

    def definition(self, value=None):
        if value is not None:
            self._definition = value
        if not hasattr(self, '_definition'):
            self._definition = False
        return self._definition

    def populate(self):

        widget = self.widget()
        contextManager = self.contextManager()

        if self.shouldAllowEdit():
            self.setWindowTitle('Edit definition')
        else:
            self.setWindowTitle('View definition')

        comboBoxExecutableType = widget.comboBoxExecutableType 
        executableTypes = contextManager.getExecutableTypes()
        comboBoxExecutableType.addItems(executableTypes)

        # update all gui items with the values from the definition
        pomsetContext = self.pomsetContext()
        definition = self.definition()

        textEditName = widget.textEditName
        textEditName.setText(definition.name() or '')
        textEditDescription =widget.textEditDescription
        textEditDescription.setText(definition.description() or '')
        
        executable = definition.executable()
        executableType = contextManager.getTypeForExecutable(executable)
        index = comboBoxExecutableType.findText(executableType)
        if index >= 0:
            comboBoxExecutableType.setCurrentIndex(index)

        self.updateGuiForEditingExecutableType(executableType)

        self.populateParameters()

        if not self.shouldAllowEdit():
            comboBoxExecutableType.setEditable(False)
            comboBoxExecutableType.setEnabled(False)
            textEditName.setReadOnly(True)
            textEditDescription.setReadOnly(True)
        return


    def updateGuiForEditingExecutableType(self, executableType):

        widget = self.widget()
        contextManager = self.contextManager()
        pomsetContext = self.pomsetContext()
        definition = self.definition()


        executable = definition.executable()
        if executable is None or \
           not contextManager.getTypeForExecutable(executable) == executableType:
            executableClass = contextManager.getClassForExecutableType(executableType)
            executable = executableClass()

        visibilityValues = []
        if executableType == 'Shell':
            # turn off unnecessary widgets and
            # turn on necessary widgets
            visibilityValues = [True, True,
                                True,
                                False, False,
                                False, False,
                                True, True]
            widget.textEditExecutablePath.setText(os.path.sep.join(executable.path()))
            widget.checkBoxStageable.setChecked(executable.stageable())
            widget.textEditStaticArgs.setText(' '.join(executable.staticArgs()))
            pass
        elif executableType == 'Hadoop Jar':
            # turn off unnecessary widgets
            # turn on necessary widgets
            visibilityValues = [False, False,
                                False,
                                True, True,
                                True, True,
                                False, False]
            widget.textEditJarFile.setText(' '.join(executable.jarFile()))
            widget.textEditJarClass.setText(' '.join(executable.jarClass()))
            widget.textEditStaticArgs.setText(' '.join(executable.staticArgs()))
            pass
        elif executableType == 'Hadoop Streaming':
            # turn off unnecessary widgets
            # turn on necessary widgets
            visibilityValues = [False, False,
                                False,
                                False, False,
                                False, False,
                                False, False]
            pass
        elif executableType == 'Hadoop Pipes':
            # turn off unnecessary widgets
            # turn on necessary widgets

            visibilityValues = [True, True,
                                False,
                                False, False,
                                False, False,
                                False, False]
            widget.textEditExecutablePath.setText(os.path.sep.join(executable.pipesFile()))
            pass


        childWidgets = [widget.labelExecutablePath,
                        widget.textEditExecutablePath,
                        widget.checkBoxStageable,
                        widget.labelJarFile,
                        widget.textEditJarFile,
                        widget.labelJarClass,
                        widget.textEditJarClass,
                        widget.labelStaticArgs,
                        widget.textEditStaticArgs]
        for visibilityValue, childWidget in zip(visibilityValues,
                                                childWidgets):
            childWidget.setVisible(visibilityValue)
            pass

        if not self.shouldAllowEdit():
            widget.textEditExecutablePath.setReadOnly(True)
            widget.checkBoxStageable.setEnabled(False)
            widget.textEditJarFile.setReadOnly(True)
            widget.textEditJarClass.setReadOnly(True)
            widget.textEditStaticArgs.setReadOnly(True)

        return


    def populateParameters(self):

        widget = self.widget()
        contextManager = self.contextManager()
        pomsetContext = self.pomsetContext()
        definition = self.definition()

        tableParameters = widget.tableParameters
        while tableParameters.rowCount():
            tableParameters.removeRow(0)

        tableParameters.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        tableParameters.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        tableParameters.setColumnWidth(0, 200)
        tableParameters.setColumnWidth(1, 120)

        parametersTable = definition.parametersTable()
        filter = RelationalModule.ColumnValueFilter(
            'parameter',
            FilterModule.ObjectKeyMatchesFilter(
                filter = FilterModule.EquivalenceFilter(ParameterModule.PORT_TYPE_DATA),
                keyFunction=lambda x: x.portType()
            )
        )
        parameters = RelationalModule.Table.reduceRetrieve(
            parametersTable,
            filter,
            ['parameter'],
            []
        )

        tableParameters.setRowCount(len(parameters))
        # tableParameters.setColumnCount(2)
        for rowIndex, parameter in enumerate(parameters):
            name = parameter.id() or ''
            item = QtGui.QTableWidgetItem('name')
            item.setData(Qt.UserRole, parameter)
            item.setData(Qt.DisplayRole, name)
            tableParameters.setItem(rowIndex, 0, item)

            direction = parameter.portDirection()
            if parameter.getAttribute(ParameterModule.PORT_ATTRIBUTE_ISSIDEEFFECT):
                direction = 'output'
            item = QtGui.QTableWidgetItem('direction')
            item.setData(Qt.UserRole, parameter)
            item.setData(Qt.DisplayRole, direction)
            tableParameters.setItem(rowIndex, 1, item)
            pass

        return


    @pyqtSlot(QtGui.QAbstractButton)
    def on_buttonBox_clicked(self, button):
        widget = self.widget()
        buttonRole = widget.buttonBox.buttonRole(button)
        if buttonRole == QtGui.QDialogButtonBox.ApplyRole:
            if self.shouldAllowEdit():
                self.saveValues()
            pass
        if buttonRole == QtGui.QDialogButtonBox.AcceptRole:
            if self.shouldAllowEdit():
                self.saveValues()
            self.accept()
            pass
        if buttonRole == QtGui.QDialogButtonBox.RejectRole:
            self.reject()
            pass
        return

    @pyqtSlot(QModelIndex)
    def on_tableParameters_doubleClicked(self, index):

        parameter = index.data(Qt.UserRole).toPyObject()
        self.displayParameter(parameter)

        return


    @pyqtSlot(str)
    def on_comboBoxExecutableType_currentIndexChanged(self, value):
        self.updateGuiForEditingExecutableType(value)
        return

    @pyqtSlot()
    def on_buttonAdd_clicked(self):

        if not self.shouldAllowEdit():
            return

        contextManager = self.contextManager()
        pomsetContext = self.pomsetContext()
        definition = self.definition()

        name = '_'.join(['parameter', uuid.uuid4().hex[:3]])

        builder = contextManager.pomsetBuilder()

        attributes = {
            'direction':ParameterModule.PORT_DIRECTION_INPUT
            }

        builder.addPomsetParameter(definition, name, attributes)

        self.populateParameters()

        return


    @pyqtSlot()
    def on_buttonEdit_clicked(self):
        contextManager = self.contextManager()

        tableParameters = self.widget().tableParameters
        parameters = list(set([x.data(Qt.UserRole).toPyObject() 
                               for x in tableParameters.selectedItems()]))

        if len(parameters) is 0:
            return

        parameterToEdit = parameters[0]

        self.displayParameter(parameterToEdit)

        return

    def displayParameter(self, parameter):

        contextManager = self.contextManager()

        # import the modules
        import pomsets_app.gui.qt.edit_parameter.widget as WidgetModule
        import pomsets_app.gui.qt.edit_parameter.controller as ControllerModule

        # initialize the widget
        controller = ControllerModule.Controller(self)
        controller.shouldAllowEdit(self.shouldAllowEdit())
        controller.contextManager(contextManager)
        controller.pomsetContext(self.pomsetContext())
        controller.parameter(parameter)
        controller.definition(self.definition())

        ui = WidgetModule.Ui_Dialog()
        ui.setupUi(controller)

        controller.widget(ui)

        # populate the dialog
        controller.populate()

        QObject.connect(contextManager.mainWindow(), 
                        SIGNAL("OnPomsetModified(PyQt_PyObject)"),
                        self.populateParameters)

        controller.show()

        return

    @pyqtSlot()
    def on_buttonRemove_clicked(self):

        if not self.shouldAllowEdit():
            return

        contextManager = self.contextManager()
        builder = contextManager.pomsetBuilder()
        pomsetContext = self.pomsetContext()
        pomset = self.definition()

        tableParameters = self.widget().tableParameters
        parameters = list(set([x.data(Qt.UserRole).toPyObject() 
                               for x in tableParameters.selectedItems()]))

        if len(parameters):
            for parameter in parameters:
                builder.removePomsetParameter(pomset, parameter.id())
            self.populateParameters()
            contextManager.mainWindow().emit(
                SIGNAL("OnPomsetModified(PyQt_PyObject)"), pomsetContext)

        return

    def saveValues(self):

        widget = self.widget()
        contextManager = self.contextManager()
        pomsetContext = self.pomsetContext()
        definition = self.definition()
        
        hasBeenModified = False
        
        name = str(widget.textEditName.text())
        if not name == definition.name():
            definition.name(name)
            hasBeenModified = True

        description = str(widget.textEditDescription.text())
        if not description == definition.description():
            definition.description(description)
            hasBeenModified = True


        executableType = str(widget.comboBoxExecutableType.currentText())
        executable = definition.executable()
        currentExecutableType = contextManager.getTypeForExecutable(executable)
        if not executableType == currentExecutableType:
            executableClass = contextManager.getClassForExecutableType(executableType)
            executable = executableClass()
            definition.executable(executable)
            hasBeenModified = True
            
        if executableType == 'Shell':
            executablePath = str(widget.textEditExecutablePath.text()).split(os.path.sep)
            if not executablePath == executable.path():
                executable.path(executablePath)
                hasBeenModified = True

            isStageable = widget.checkBoxStageable.isChecked()
            if not executable.stageable() == isStageable:
                executable.stageable(isStageable)
                hasBeenModified = True

            staticArgs = str(widget.textEditStaticArgs.text()).split(' ')
            if not executable.staticArgs() == staticArgs:
                executable.staticArgs(staticArgs)
                hasBeenModified = True

        elif executableType == 'Hadoop Jar':

            jarFile = str(widget.textEditJarFile.text()).split(' ')
            if not executable.jarFile() == jarFile:
                executable.jarFile(jarFile)
                hasBeenModified = True

            jarClass = str(widget.textEditJarClass.text()).split(' ')
            if not executable.jarClass() == jarClass:
                executable.jarClass(jarClass)
                hasBeenModified = True
            pass

        elif executableType == 'Hadoop Streaming':
            executable.jarFile([contextManager.getHadoopStreamingJar()])
            executable.jarClass([])
            pass

        elif executableType == 'Hadoop Pipes':

            pipesFile = str(widget.textEditExecutablePath.text()).split(os.path.sep)
            if not executable.pipesFile() == pipesFile:
                executable.pipesFile(pipesFile)
                hasBeenModified = True
            pass

        if hasBeenModified:

            pomsetContext.isModified(True)
            
            contextManager.mainWindow().emit(
                SIGNAL("OnPomsetModified(PyQt_PyObject)"), pomsetContext)
        return

    # END class Controller
    pass
