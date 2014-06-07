from StringIO import StringIO
from PyQt4 import QtCore, QtGui, QtWebKit
from PyQt4.QtCore import QUrl, QObject, SIGNAL, QThread, QString
from PyQt4.QtGui import QPrinter, QApplication
from PyQt4.QtWebKit import QWebView, QWebSettings
from pyPdf.pdf import PdfFileWriter, PdfFileReader

import datetime
import os
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from utils.Regex import Regex


__author__ = 'Rabbi'

class WebPageToPdf(QObject):
    threadPdfStatusBar = QtCore.pyqtSignal(object)
    threadPdfWritingStatus = QtCore.pyqtSignal(object)
    threadPdfWritingDone = QtCore.pyqtSignal(int)

    def __init__(self):
        QObject.__init__(self)
        self.regex = Regex()
        self.title = ''
        self.webView = QWebView()
        self.webView.settings().setAttribute(QWebSettings.AutoLoadImages, True)
        self.webView.settings().setAttribute(QWebSettings.JavascriptEnabled, True)
        self.webView.settings().setAttribute(QWebSettings.PluginsEnabled, True)
        self.webView.settings().setAttribute(QWebSettings.DeveloperExtrasEnabled, True)
        self.pdfPrinter = QPrinter()
        self.webView.loadFinished.connect(self.convertToPdf)


    def setupDefaultPdfPrinter(self, fileName):
        self.pdfPrinter.setOrientation(QPrinter.Portrait)
        self.pdfPrinter.setPageSize(QPrinter.A4)
        self.pdfPrinter.setOutputFormat(QPrinter.PdfFormat)
        self.pdfPrinter.setOutputFileName(fileName)

    def printWebHtmlToPdf(self, url, filePath, fileName, groupType):
        self.tempPdfFile = filePath + 'out.pdf'
        self.filePath = filePath
        self.fileName = fileName
        self.url = url
        self.groupType = groupType
        self.setupDefaultPdfPrinter(self.tempPdfFile)
        self.threadPdfStatusBar.emit('Fetching Data From Web. Please Wait...')
        #        self.threadPdfWritingStatus.emit(
        #            '<font size=4 color=green><b>Method "%s": </b></font><font color=green><b>Fetching Data From Web for</b> %s<b>.<br />Please Wait...</b></font>' % (
        #                self.groupType, self.url))
        self.threadPdfWritingStatus.emit(
            '<font color=green><b>Fetching Data From Web for</b> %s<b>.<br />Please Wait...</b></font>' % self.url)
        self.webView.load(QUrl(url))
        self.title = self.webView.title()

    def convertToPdf(self):
        print 'Generating Pdf'
        #        self.threadPdfWritingStatus.emit(
        #            '<font size=4><b>Method "%s": </b></font><b>Generating Pdf for</b> %s<b>. Please Wait...</b>' % (
        #                self.groupType, self.url))
        self.threadPdfWritingStatus.emit(
            '<b>Generating Pdf for</b> %s<b>. Please Wait...</b>' % self.url)
        self.threadPdfStatusBar.emit('Generating Pdf. Please Wait...')
        self.webView.print_(self.pdfPrinter)
        print 'Generated Pdf'
        #        self.threadPdfWritingStatus.emit(
        #            '<font size=4><b>Method "%s": </b></font><b>Generated Pdf for</b> %s<b>. Please Wait...</b>' % (
        #                self.groupType, self.url))
        self.threadPdfWritingStatus.emit(
            '<b>Generated Pdf for</b> %s<b>. Please Wait...</b>' % self.url)
        self.threadPdfStatusBar.emit('Generated Pdf.')
        self.mergePdf()
        self.threadPdfWritingDone.emit(True)

    def mergePdf(self):
    #        self.threadPdfWritingStatus.emit(
    #            '<font size=4><b>Method "%s": </b></font><b>Setting Title for</b> %s<b>. Please Wait...</b><br />' % (
    #                self.groupType, self.url))
        self.threadPdfWritingStatus.emit(
            '<b>Setting Title for</b> %s<b>. Please Wait...</b><br />' % self.url)

        packet = StringIO()
        # create a new PDF with Reportlab
        pdfCanvas = canvas.Canvas(packet, pagesize=A4)
        pdfCanvas.setFont('Helvetica', 8)
        if len(self.title) is 0:
            self.title = str(self.url).split('/')[-1]
            self.title = self.regex.getSearchedData('(?i)([a-zA-Z0-9-_ ]*?)\.[a-zA-Z0-9_]*$', self.title)
            self.title = self.regex.replaceData('(?i)_', ' ', self.title)
        title = unicode(self.title[:57] + '...') if  (len(self.title) > 60) else unicode(self.title)
        url = self.url[:57] + '...' if (len(self.title) > 60) else self.url
        pdfCanvas.drawString(5, 830, title + '                      ' + str(url).lower())
        d = datetime.datetime.now()
        strDate = str(d.strftime("%Y-%m-%d %H-%M-%S %p"))
        pdfCanvas.drawString(420, 5, 'Created Date Time: ' + strDate)
        pdfCanvas.save()
        packet.seek(0)
        newPdf = PdfFileReader(packet)

        if not os.path.exists(self.tempPdfFile):
            return self.printWebHtmlToPdf(self.url, self.filePath, self.fileName)

        writer = PdfFileWriter()
        tmpPdfFile = file(self.tempPdfFile, 'rb')
        reader = PdfFileReader(tmpPdfFile)
        for i in range(0, (reader.getNumPages())):
            page = reader.getPage(i)
            page.mergePage(newPdf.getPage(0))
            #            page = newPdf.getPage(0)
            #            page.mergePage(reader.getPage(i))
            writer.addPage(page)
        print 'Filename: ' + self.fileName
        outputStream = file(self.filePath + self.fileName, "wb")
        writer.write(outputStream)
        outputStream.close()
        tmpPdfFile.close()
        os.remove(str(self.tempPdfFile))


