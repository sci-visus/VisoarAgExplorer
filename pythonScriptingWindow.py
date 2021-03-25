
from VisoarSettings         import *
from slam2dWidget 				import *

class PythonScriptWindow(QDialog):
    def __init__(self, parent):
        super(PythonScriptWindow, self).__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.parent = parent
        self.DEBUG = True
        self.scriptNames = EXPERIMENTAL_SCRIPT_LIST  # MASTER_SCRIPT_LIST
        self.viewer = parent.viewer
        self.viewer2 = parent.viewer2
        self.app_dir = self.parent.app_dir

        # self.central_widget = QFrame()
        # self.central_widget.setFrameShape(NoFrame)

        self.setStyleSheet(LOOK_AND_FEEL)
        self.setWindowFlags(
            self.windowFlags() | Qt.WindowStaysOnTopHint)  # set always on top flag, makes window disappear

        # self.layout= QGridLayout()
        # self.layout.setColumnStretch(1, 1)
        # self.layout.setColumnStretch(2, 2)
        # self.layout.setSpacing(2)

        # self.baseLayout.addLayout(self.layout)

        # self.toolbar=QVBoxLayout()
        self.bottomButtonsLayout = QHBoxLayout()

        self.toolbar = QVBoxLayout()
        self.toolbar.setSpacing(10)

        # self.baseLayout.addLayout(self.toolbar)

        self.inputModeATabLabel = QLabel("Sensor:", self)

        self.comboBoxScripts = QComboBox(self)
        self.addScriptActionComboboxForEdits(self.comboBoxScripts)

        self.pythontextbox = QTextEdit(self)
        # self.pythontextbox.setText(getTextFromScript(TGI_script))
        mpath = os.path.join('scripts', 'Original.py')
        self.pythontextbox.setText(getTextFromScript(mpath))

        # self.pythontextbox.move(20, layoutOffset)
        self.pythontextbox.resize(480, 440)
        # layoutOffset += 20 + 440

        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.pythontextbox.sizePolicy().hasHeightForWidth())
        # self.pythontextbox.setSizePolicy(sizePolicy)
        self.pythontextbox.setStyleSheet(MY_SCROLL_LOOK)
        if SHOW_OUTPUT_BOX:
            self.outpythontextbox = QTextEdit(self)
            # self.pythontextbox.setText(getTextFromScript(TGI_script))
            # self.outpythontextbox.setText(getTextFromScript(COUNT_SCRIPT))
            # self.outpythontextbox.move(20, layoutOffset)
            self.outpythontextbox.resize(480, 100)
            # self.outpythontextbox.setSizePolicy(sizePolicy)
            self.outpythontextbox.setStyleSheet(MY_OUTPUT_LOOK)

        # Create a button in the window
        self.pythonbutton = QPushButton('', self)
        self.pythonbutton.adjustSize()

        # Create a button in the window
        self.closebutton = QPushButton('', self)

        # connect button to function on_click
        self.pythonbutton.clicked.connect(self.on_run)
        mpath = os.path.join('icons', 'Go.png')
        self.pythonbutton.setIcon(QIcon(mpath))

        self.closebutton.clicked.connect(self.on_close)
        self.closebutton.setIcon(QIcon('icons/Close.png'))

        self.pythonbutton.setStyleSheet("""background-color: #045951;""")
        self.closebutton.setStyleSheet("""background-color: #045951;""")

        self.pythonbutton.setIconSize(QSize(30, 30))
        self.pythonbutton.resize(40, 40)
        self.pythonbutton.setFixedSize(50, 50);

        self.closebutton.setIconSize(QSize(30, 30))
        self.closebutton.resize(40, 40)
        self.closebutton.setFixedSize(50, 50);

        self.toolbar.addWidget(self.comboBoxScripts)
        self.toolbar.addWidget(self.pythontextbox)
        if SHOW_OUTPUT_BOX:
            self.toolbar.addWidget(self.outpythontextbox)
        # self.toolbar.addWidget(self.pythonbutton, 4, 0)
        # self.toolbar.addWidget(self.closebutton, 4, 1)

        self.bottomButtonsLayout.addWidget(self.pythonbutton)
        self.bottomButtonsLayout.addWidget(self.closebutton)
        self.toolbar.addLayout(self.bottomButtonsLayout)

        self.setLayout(self.toolbar)

        self.setGeometry(300, 300, 440, 900)

    def addScriptActionComboboxForEdits(self, cbox):

        for item in self.scriptNames:
            cbox.addItem(item)

        cbox.setStyleSheet(MY_COMBOX)
        cbox.currentIndexChanged.connect(self.insertScriptIntoTextEditBox)

    def insertScriptIntoTextEditBox(self):
        self.app_dir = self.parent.app_dir
        # filename  = self.app_dir + '/scripts/'+self.comboBoxScripts.currentText() +'.py'
        filename = os.path.join(self.app_dir, 'scripts', self.comboBoxScripts.currentText() + '.py')
        x = getTextFromScript(filename)
        self.pythontextbox.setText(x)

    def on_run(self):
        print("on_click for pythonScriptingWindow")
        script = self.pythontextbox.toPlainText().strip() + '\n'
        # script = """output = input"""
        if script:
            print('-------------SCRIPT STARTS BELOW -------------------')
            print(script)
            print('-------------  SCRIPT ENDS ABOVE -------------------')
            fieldname = "output=ArrayUtils.interleave(ArrayUtils.split(voronoi())[0:3])"
            print("Running script ")
            # print(self.projDir)
            #self.viewer.setFieldName(fieldname)
            #script_output = self.viewer.setScriptingCode(script)
            self.viewer2.setFieldName(fieldname)
            script_output = self.viewer2.setScriptingCode(script)
            # self.outpythontextbox.setText(script_output)

            if self.DEBUG:
                print('run script finished')
        # parent.runScript(script)
        print("end on_click for pythonScriptingWindow")

    # self.hide()

    def on_close(self):
        self.hide()
        self.update()

    def on_show(self):
        self.show()
        self.raise_()
        self.activateWindow()