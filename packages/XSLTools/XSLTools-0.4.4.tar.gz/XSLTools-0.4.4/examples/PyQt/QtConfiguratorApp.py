#!/usr/bin/env python

from qt import QApplication, QMainWindow, QScrollView, QSizePolicy
import QtConfigurator
import sys

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = QScrollView()
    configurator = QtConfigurator.get_resource("PyQt", window)
    window.addChild(configurator)
    window.show()
    window.resize(
        configurator.width(), # + window.verticalScrollBar().width(),
        configurator.height()) # + window.horizontalScrollBar().height())
    app.setMainWidget(window)
    app.exec_loop()

# vim: tabstop=4 expandtab shiftwidth=4
