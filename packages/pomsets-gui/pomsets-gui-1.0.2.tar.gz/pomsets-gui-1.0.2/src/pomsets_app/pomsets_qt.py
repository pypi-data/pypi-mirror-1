
import pomsets_app.gui.qt.application as ApplicationModule


from PyQt4 import QtGui



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


    app = ApplicationModule.Application(['pomsets'])

    app.runProgram()

    return

if __name__=="__main__":
    main()

