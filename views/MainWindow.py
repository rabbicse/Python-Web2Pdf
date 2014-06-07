from time import sleep
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import QString, Qt, QDir
from PyQt4.QtGui import *
import sys
from utils.Regex import Regex
from works.WebPageToPdf import WebPageToPdf
import os
import time
import datetime

__author__ = 'Rabbi'


class MainForm(QMainWindow):
    def __init__(self, parent=None):
        super(MainForm, self).__init__(parent)
        self.regex = Regex()
        self.alreadyClickedA = False
        self.alreadyClickedB = False
        self.fileDir = None
        self.fileDirB = None
        self.fileName = None
        self.fileNameB = None
        self.totalUrlA = 0
        self.totalUrlB = 0
        self.currentUrlA = 0
        self.currentUrlB = 0
        self.pdfCounter = 1
        self.pdfCounterB = 1
        self.typeName = 'B'
        self.setupUI()

    def setupUI(self):
        self.isActionEvent = False

        ## Web URL
        self.labelUrl = QLabel('<font size=4><b>Select text File with url List: </b></font>')
        self.labelUrl.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.labelUrl.setFixedWidth(200)
        self.btnUrlList = QPushButton('&Browse')
        self.btnUrlList.setFont(QFont('Helvetica', 8, QFont.Bold))
        self.btnUrlList.setFixedWidth(100)
        self.btnUrlList.clicked.connect(self.urlListSelected)
        self.labelSelectedUrl = QLabel()
        self.labelSelectedUrl.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        layoutUrl = QHBoxLayout()
        layoutUrl.addWidget(self.btnUrlList)
        layoutUrl.addWidget(self.labelSelectedUrl)

        ## File Path
        self.labelPdfPath = QLabel('<font size=4><b>Select Pdf Path: </b></font>')
        self.labelPdfPath.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.labelPdfPath.setFixedWidth(200)
        self.btnOpenPdfDir = QPushButton('&Browse')
        self.btnOpenPdfDir.setFont(QFont('Helvetica', 8, QFont.Bold))
        self.btnOpenPdfDir.setFixedWidth(100)
        self.btnOpenPdfDir.clicked.connect(self.pdfPathSelected)
        self.labelSelectedPath = QLabel()
        self.labelSelectedPath.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        layoutPath = QHBoxLayout()
        layoutPath.addWidget(self.btnOpenPdfDir)
        layoutPath.addWidget(self.labelSelectedPath)

        self.labelGrouping = QLabel('<font size=4><b>"Raw Numbering" and "Group Similar URLs" (A and B): </b></font>')
        self.labelGrouping.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.comboGrouping = QComboBox()
        self.comboGrouping.setFont(QFont('Helvetica', 8, QFont.Bold))
        self.comboGrouping.setFixedWidth(100)
        self.comboGrouping.addItem('B')
        self.comboGrouping.addItem('A')
        self.comboGrouping.activated[str].connect(self.onActivated)
        layoutComboGrouping = QHBoxLayout()
        layoutComboGrouping.addWidget(self.comboGrouping)
        #        layoutComboGrouping.addWidget(self.btnGroupingHelp)

        self.btnPrintPdf = QPushButton('&Start')
        self.btnPrintPdf.setFixedWidth(100)
        self.btnPrintPdf.setFont(QFont('Helvetica', 8, QFont.Bold))
        self.btnPrintPdf.clicked.connect(self.printPdfAction)
        self.btnClear = QPushButton('&Clear Results')
        self.btnClear.setFont(QFont('Helvetica', 8, QFont.Bold))
        self.btnClear.setFixedWidth(100)
        self.btnClear.clicked.connect(self.clearAll)
        self.btnGroupingHelp = QPushButton('&Help')
        self.btnGroupingHelp.setFont(QFont('Helvetica', 8, QFont.Bold))
        self.btnGroupingHelp.setFixedWidth(100)
        self.btnGroupingHelp.clicked.connect(self.groupingHelpAction)
        layoutAction = QHBoxLayout()
        layoutAction.addWidget(self.btnPrintPdf)
        layoutAction.addWidget(self.btnClear)
        layoutAction.addWidget(self.btnGroupingHelp)

        layoutTop = QGridLayout()
        layoutTop.addWidget(self.labelUrl, 0, 0)
        layoutTop.addLayout(layoutUrl, 0, 1, Qt.AlignLeft)
        layoutTop.addWidget(self.labelPdfPath, 1, 0)
        layoutTop.addLayout(layoutPath, 1, 1, Qt.AlignLeft)
        #        layoutTop.addWidget(self.labelGrouping, 2, 0)
        #        layoutTop.addLayout(layoutComboGrouping, 2, 1, Qt.AlignLeft)
        #        layoutTop.addWidget(self.btnClear, 3, 0, Qt.AlignRight)
        layoutTop.addLayout(layoutAction, 2, 1, Qt.AlignLeft)


        ## Bottom Portion
        self.labelProStatusA = QLabel()
        self.labelProStatusB = QLabel()

        self.labelWebAddress = QLabel('<b>Current URL Being Processed:</b>')
        self.lineEditWebAddress = QLineEdit()
        self.lineEditWebAddress.setReadOnly(True)
        self.labelStatus = QLabel('<b>Pdf Generation Status:</b>')
        self.textBrowserStatus = QTextBrowser()
        self.textBrowserStatus.setReadOnly(True)
        layout = QVBoxLayout()
        #        layout.addLayout(layoutUrl)
        #        layout.addLayout(layoutPath)
        layout.addLayout(layoutTop)
        layout.addWidget(self.labelProStatusA)
        layout.addWidget(self.labelProStatusB)
        layout.addWidget(self.labelWebAddress)
        layout.addWidget(self.lineEditWebAddress)
        layout.addWidget(self.labelStatus)
        layout.addWidget(self.textBrowserStatus)

        widget = QWidget()
        widget.setLayout(layout)

        self.setCentralWidget(widget)
        self.statusBar().showMessage(QString("Application Started...."), 500)
        self.setWindowTitle('PDF Batch Saver')
        self.setWindowFlags(Qt.WindowCloseButtonHint | Qt.WindowMinimizeButtonHint)
        screen = QDesktopWidget().screenGeometry()
        #        self.setFixedSize((screen.width() / 2) + 150, (screen.height() / 2) + 150)
        self.resize((screen.width() / 2) + 150, (screen.height() / 2) + 150)

    def printPdfAction(self):
        if self.fileName is not None and self.fileDir is not None and self.alreadyClickedA is False and self.typeName == 'A':
            self.webToPdf = WebPageToPdf()
            self.webToPdf.threadPdfStatusBar.connect(self.showStatus)
            self.webToPdf.threadPdfWritingStatus.connect(self.appendStatus)
            self.webToPdf.threadPdfWritingDone.connect(self.pdfGenFinished)
            f = open(self.fileName, 'rb')
            self.lists = f.readlines()
            f.close()
            self.totalUrlA = len(self.lists)
            self.alreadyClickedA = True
            self.pdfGenFinished()
        elif self.fileNameB is not None and self.fileDirB is not None and self.alreadyClickedB is False and self.typeName == 'B':
            self.webToPdfB = WebPageToPdf()
            self.webToPdfB.threadPdfStatusBar.connect(self.showStatus)
            self.webToPdfB.threadPdfWritingStatus.connect(self.appendStatus)
            self.webToPdfB.threadPdfWritingDone.connect(self.pdfGenFinishedB)
            f = open(self.fileNameB, 'rb')
            self.listsB = f.readlines()
            f.close()
            pdfFiles = [f for f in os.listdir(self.fileDirB) if f.endswith('.pdf')]
            if len(pdfFiles) > 0:
                self.pdfCounterB = int(self.regex.getSearchedData('(?i)^(\d+)_', pdfFiles[-1])) + 1
            self.totalUrlB = len(self.listsB)
            self.alreadyClickedB = True
            self.startTime = time.clock()
            self.pdfGenFinishedB()
        else:
            QMessageBox.warning(None, 'Warning', 'Please Select your URL List and PDF writing Path.')

    def pdfGenFinished(self):
        if self.lists is not None and len(self.lists) > 0:
            self.currentUrlA += 1
            url = self.lists.pop(0)
            self.lineEditWebAddress.setText(url)
            url = url.strip()
            self.labelProStatusA.setText(
                '<font color="green" size=4><b>For grouping "A": <u> %s </u> total items in the batch, processing <u> %s </u> out of <u> %s </u></b></font>' % (
                    str(
                        self.totalUrlA), str(self.currentUrlA), str(self.totalUrlA)))

            pdfFile = str(url).split('/')[-1]
            print 'pdf file : ' + pdfFile
            pdfFile = self.regex.getSearchedData('(?i)([a-zA-Z0-9-_ ]*?)\.[a-zA-Z0-9_]*$', pdfFile)
            pdfFiles = [f for f in os.listdir(self.fileDir) if f.endswith('.pdf')]
            finalPdfFile = ''
            i = 2
            for file in pdfFiles:
                if self.regex.isFoundPattern('(?i)' + pdfFile, file):
                    index = self.regex.getSearchedData('(?i)(\d+).*?$', file)
                    finalPdfFile = str(index) + '_' + str(pdfFile) + '_copy_' + str(i) + '.pdf'
                    i += 1

            if len(finalPdfFile) is 0:
                finalPdfFile = str(self.pdfCounter) + '_' + pdfFile + '.pdf'
            else:
                self.pdfCounter -= 1

            self.webToPdf.printWebHtmlToPdf(url, self.fileDir + '/', finalPdfFile, 'A')
            self.pdfCounter += 1
        else:
            self.showStatus('Pdf Generation Completed')
            self.alreadyClicked = False
            self.totalUrlA = 0
            self.currentUrlA = 0
            #            self.labelProStatusA.setText('')

    def pdfGenFinishedB(self):
        if self.listsB is not None and len(self.listsB) > 0:
            self.currentUrlB += 1
            url = self.listsB.pop(0)
            self.lineEditWebAddress.setText(url)
            url = url.strip()
            #            self.labelProStatusB.setText(
            #                '<font color="green" size=4><b>For grouping "B": <u> %s </u> total items in the batch, processing <u> %s </u> out of <u> %s </u></b></font>' % (
            #                    str(
            #                        self.totalUrlB), str(self.currentUrlB), str(self.totalUrlB)))
            elapsedTime = time.clock() - self.startTime
            print elapsedTime
            self.labelProStatusB.setText(
                '<font size=4><b>URL <u> %s </u> of <u> %s </u> being processed. Time elapsed: %s</b></font>' % (
                    str(self.currentUrlB), str(self.totalUrlB),
                    str(time.strftime('%H:%M:%S', time.gmtime(elapsedTime)))))

            pdfFile = str(url).split('/')[-1]
            print 'pdf file : ' + pdfFile
            #            pdfFile = self.regex.getSearchedData('(?i)/([a-zA-Z0-9-_. ]*)$', url)
            pdfFile = self.regex.getSearchedData('(?i)([a-zA-Z0-9-_ ]*?)\.[a-zA-Z0-9_]*$', pdfFile)
            pdfFiles = [f for f in os.listdir(self.fileDirB) if f.endswith('.pdf')]
            #            self.pdfCounterB = int(self.regex.getSearchedData('(?i)^(\d+)_', pdfFiles[-1]))
            finalPdfFile = ''
            i = 2
            for file in pdfFiles:
                if self.regex.isFoundPattern('(?i)' + pdfFile, file):
                    finalPdfFile = str(self.pdfCounterB) + '_' + str(pdfFile) + '_copy_' + str(i) + '.pdf'
                    i += 1

            if len(finalPdfFile) is 0:
                finalPdfFile = str(self.pdfCounterB) + '_' + pdfFile + '.pdf'

            self.webToPdfB.printWebHtmlToPdf(url, self.fileDirB + '/', finalPdfFile, 'B')
            self.labelProStatusB.setText(
                '<font size=4><b>URL <u> %s </u> of <u> %s </u> being processed. Time elapsed: %s</b></font>' % (
                    str(self.currentUrlB), str(self.totalUrlB),
                    str(time.strftime('%H:%M:%S', time.gmtime(elapsedTime)))))
            self.pdfCounterB += 1
        else:
            self.showStatus('Pdf Generation Completed')
            self.alreadyClickedB = False
            self.totalUrlB = 0
            self.currentUrlB = 0
            self.fileDirB = None
            self.fileNameB = None
#            self.labelProStatusB.setText('')

    def urlListSelected(self):
        if self.typeName == 'A':
            self.fileName = QtGui.QFileDialog.getOpenFileName(self, "Select Text File", QDir.homePath() + "/Desktop")
        if self.typeName == 'B':
            self.fileNameB = QtGui.QFileDialog.getOpenFileName(self, "Select Text File", QDir.homePath() + "/Desktop")
            self.labelSelectedUrl.setText('<b>%s</b>' % str(self.fileNameB))

    def pdfPathSelected(self):
        if self.typeName == 'A':
            self.fileDir = QtGui.QFileDialog.getExistingDirectory(self, "Select Directory",
                QDir.homePath() + "/Desktop")
            self.pdfCounter = 1
        if self.typeName == 'B':
            self.fileDirB = QtGui.QFileDialog.getExistingDirectory(self, "Select Directory",
                QDir.homePath() + "/Desktop")
            self.pdfCounterB = 1
            self.labelSelectedPath.setText('<b>%s</b>' % str(self.fileDirB))

    def onActivated(self, text):
        self.typeName = text
        self.pdfCounter = 1

    def clearAll(self):
        self.lineEditWebAddress.clear()
        self.textBrowserStatus.clear()
        self.statusBar().showMessage('')
        self.pdfCounterB = 1
        self.labelProStatusB.setText('')
        self.fileDirB = None
        self.fileNameB = None

    def groupingHelpAction(self):
        QMessageBox.information(None, 'Help Message',
            'This program reads a text file of URLs and produces a series of PDFs. If the source text file contains more than one listing of the same URL, the program will create an extra copy of the PDF anyway in the output folder.')

    def appendStatus(self, data):
        self.textBrowserStatus.append(data)

    def showStatus(self, data):
        self.statusBar().showMessage(data)


class MainWindow:
    def __init__(self):
        pass

    def showMainWindow(self):
        application = QApplication(sys.argv)
        mainForm = MainForm()
        mainForm.show()
        application.exec_()
