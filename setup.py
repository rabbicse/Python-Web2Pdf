from distutils.core import setup
import py2exe
import glob


setup(
    windows=['Main.py'],
    options={"py2exe": {
        "includes": ["sip", "PyQt4", "PyQt4.QtGui", "PyQt4.QtCore", "PyQt4.QtWebKit", "PyQt4.QtNetwork",
                     "reportlab.pdfbase.*"]}},
    name='Phoenix',
    version='',
    packages=['works', 'logs', 'utils', 'views'],
    #    data_files=[('imageformats', ['imageformats/qgif4.dll', 'imageformats/qico4.dll', 'imageformats/qjpeg4.dll', 'imageformats/qmng4.dll'])],
    data_files=[('imageformats', glob.glob('imageformats/*.dll'))],
    url='',
    license='',
    author='Rabbi',
    author_email='',
    description=''
)
