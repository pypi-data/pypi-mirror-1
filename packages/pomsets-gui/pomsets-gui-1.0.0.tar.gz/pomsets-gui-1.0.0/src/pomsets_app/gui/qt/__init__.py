from PyQt4.QtCore import *

class Controller(object):

    def contextManager(self, value=None):
        if value is not None:
            self._contextManager = value
        if not hasattr(self, '_contextManager'):
            self._contextManager = None
        return self._contextManager

    def pomsetContext(self, value=None):
        if value is not None:
            self._pomsetContext = value
        if not hasattr(self, '_pomsetContext'):
            self._pomsetContext = None
        return self._pomsetContext

    def widget(self, value=None):
        if value is not None:
            self._widget = value
        if not hasattr(self, '_widget'):
            self._widget = None
        return self._widget

    def connectSignals(self):
        raise NotImplementedError('%s.connectSignals' % self.__class__)

    # END class Controller
    pass
