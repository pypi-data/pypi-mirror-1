# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'resources/qt/edit task dialog.ui'
#
# Created: Thu Mar  4 16:15:09 2010
#      by: PyQt4 UI code generator 4.7
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(450, 413)
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setGeometry(QtCore.QRect(70, 370, 341, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.labelName = QtGui.QLabel(Dialog)
        self.labelName.setGeometry(QtCore.QRect(30, 30, 62, 16))
        self.labelName.setObjectName("labelName")
        self.labelComment = QtGui.QLabel(Dialog)
        self.labelComment.setGeometry(QtCore.QRect(30, 70, 71, 16))
        self.labelComment.setObjectName("labelComment")
        self.labelParameters = QtGui.QLabel(Dialog)
        self.labelParameters.setGeometry(QtCore.QRect(30, 110, 91, 16))
        self.labelParameters.setObjectName("labelParameters")
        self.tableParameters = QtGui.QTableWidget(Dialog)
        self.tableParameters.setGeometry(QtCore.QRect(30, 140, 391, 211))
        self.tableParameters.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.tableParameters.setObjectName("tableParameters")
        self.tableParameters.setColumnCount(2)
        self.tableParameters.setRowCount(0)
        item = QtGui.QTableWidgetItem()
        self.tableParameters.setHorizontalHeaderItem(0, item)
        item = QtGui.QTableWidgetItem()
        self.tableParameters.setHorizontalHeaderItem(1, item)
        self.textEditName = QtGui.QLineEdit(Dialog)
        self.textEditName.setGeometry(QtCore.QRect(110, 21, 311, 31))
        self.textEditName.setObjectName("textEditName")
        self.textEditComment = QtGui.QLineEdit(Dialog)
        self.textEditComment.setGeometry(QtCore.QRect(110, 60, 311, 31))
        self.textEditComment.setObjectName("textEditComment")

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), Dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "Edit task", None, QtGui.QApplication.UnicodeUTF8))
        self.labelName.setText(QtGui.QApplication.translate("Dialog", "Name", None, QtGui.QApplication.UnicodeUTF8))
        self.labelComment.setText(QtGui.QApplication.translate("Dialog", "Comment", None, QtGui.QApplication.UnicodeUTF8))
        self.labelParameters.setText(QtGui.QApplication.translate("Dialog", "Parameters", None, QtGui.QApplication.UnicodeUTF8))
        self.tableParameters.horizontalHeaderItem(0).setText(QtGui.QApplication.translate("Dialog", "Name", None, QtGui.QApplication.UnicodeUTF8))
        self.tableParameters.horizontalHeaderItem(1).setText(QtGui.QApplication.translate("Dialog", "Sweep", None, QtGui.QApplication.UnicodeUTF8))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    Dialog = QtGui.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())

