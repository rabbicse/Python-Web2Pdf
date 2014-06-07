from PyQt4.QtGui import QApplication
from views.MainWindow import MainWindow
from works.WebPageToPdf import WebPageToPdf
import sys
__author__ = 'Rabbi'

#def WebPageToPdf():
#    webToPdf = WebPageToPdf()
#
#import sys
#from PyQt4.QtCore import *
#from PyQt4.QtGui import *
#from PyQt4.QtWebKit import *
##
#app = QApplication(sys.argv)
##
#web = QWebView()
#web.load(QUrl("http://facebook.com"))
##web.show()
#
#printer = QPrinter()
#printer.setPageSize(QPrinter.A4)
#printer.setOutputFormat(QPrinter.PdfFormat)
#printer.setOutputFileName("test.pdf")
#
#def convertIt():
#    web.print_(printer)
#    print "Pdf generated"
#    QApplication.exit()
#
#QObject.connect(web, SIGNAL("loadFinished(bool)"), convertIt)
#
#sys.exit(app.exec_())
def startMainApplication():
    mainWindow = MainWindow()
    mainWindow.showMainWindow()

if __name__ == '__main__':
    startMainApplication()