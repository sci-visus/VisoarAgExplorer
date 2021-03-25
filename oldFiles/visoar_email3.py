import smtplib, ssl, email
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


from PyQt5.QtGui                      import QFont
from PyQt5.QtCore                     import QUrl, Qt, QSize, QDir, QRect
from PyQt5.QtWidgets                  import QApplication, QHBoxLayout, QLineEdit,QLabel, QLineEdit, QTextEdit, QGridLayout
from PyQt5.QtWidgets                  import QMainWindow, QPushButton, QVBoxLayout,QSplashScreen,QProxyStyle, QStyle, QAbstractButton
from PyQt5.QtWidgets                  import QWidget, QMessageBox, QGroupBox, QShortcut,QSizePolicy,QPlainTextEdit,QDialog, QFormLayout
from PyQt5.QtWebEngineWidgets         import QWebEngineView
from PyQt5.QtWidgets                  import QTableWidget,QTableWidgetItem

from lookAndFeel                import *
#from googleAutho                import *
import yagmail
DEBUG = True
FOR_WESTON = False


REDIRECT_URI = ''

GOOGLE_CLIENT_ID = ''
GOOGLE_CLIENT_SECRET = ''
GOOGLE_REFRESH_TOKEN = None
#Fill in values from:
import visus_google.py

class VisoarImageMailer(QDialog):

    def __init__(self, img, parent):
        # super().__init__()
        QDialog.__init__(self)
        if DEBUG:
            print("In VisoarImageMailer")
        self.imgWPath = img
        self.setStyleSheet(LOOK_AND_FEEL)

        # def __init__(self, *args, **kwargs):
        #     super(VMailDialog, self).__init__(*args, **kwargs)

        if DEBUG:
            print("In VMailDialog")

        # self.setWindowTitle("ViSOAR Snapshot Emailer")
        self.layout = QVBoxLayout()
        self.InstructionsLabel = QLabel('Email the ViSOAR Ag Explorer screencapture:')

        if 0:
            self.loginWithGoogle = QPushButton('Login With Google', self)
            # self.buttons.create_project.move(20,80)
            # self.create_project.resize(180,80)
            self.loginWithGoogle.setStyleSheet(GREEN_PUSH_BUTTON)
            self.layout.addWidget(self.loginWithGoogle, alignment=Qt.AlignCenter)
            self.loginWithGoogle.clicked.connect(self.AOAuthorizeGmailAccount)

        if 1:
            self.detailsBox = QGroupBox('Email:')
            self.detailsBox.setStyleSheet(QGROUPBOX_LOOK_AND_FEEL)

            self.sublayoutForm = QFormLayout()

            self.FromLabel = QLabel('From:')
            self.FromTextbox = QLineEdit(self)
            if DEBUG:
                self.FromTextbox.setText('amy@visus.net')
            elif FOR_WESTON:
                self.FromTextbox.setText('dronepilot@visus.net')

            self.FromTextbox.move(20, 20)
            self.FromTextbox.resize(180, 40)
            self.FromTextbox.setStyleSheet(
                "padding:10px; background-color: #e6e6e6; color: rgb(0, 0, 0);  border: 2px solid #09cab8")
            self.sublayoutForm.addRow(self.FromLabel, self.FromTextbox)

            self.FromLabel = QLabel('From:')
            self.FromTextbox = QLineEdit(self)
            if DEBUG:
                self.FromTextbox.setText('amy@visus.net')
            elif FOR_WESTON:
                self.FromTextbox.setText('dronepilot@visus.net')

            self.PasswordLabel = QLabel('Password:')
            self.PasswordTextbox = QLineEdit(self)
            self.PasswordTextbox.setEchoMode(QLineEdit.Password)
            self.PasswordTextbox.move(20, 20)
            self.PasswordTextbox.resize(180, 40)
            self.PasswordTextbox.setStyleSheet(
                "padding:10px; background-color: #e6e6e6; color: rgb(0, 0, 0);  border: 2px solid #09cab8")
            self.sublayoutForm.addRow(self.PasswordLabel, self.PasswordTextbox)

            self.ToLabel = QLabel('To:')
            self.ToTextbox = QLineEdit(self)
            self.ToTextbox.move(20, 20)
            self.ToTextbox.resize(180, 40)
            self.ToTextbox.setStyleSheet(
                "padding:10px; background-color: #e6e6e6; color: rgb(0, 0, 0);  border: 2px solid #09cab8")
            self.sublayoutForm.addRow(self.ToLabel, self.ToTextbox)
            if DEBUG:
                self.ToTextbox.setText('amy.a.gooch@gmail.com')
            elif FOR_WESTON:
                self.ToTextbox.setText('lramthun@gmail.com')

            self.SubjectLabel = QLabel('Subject:')
            self.SubjectTextbox = QLineEdit(self)
            self.SubjectTextbox.move(20, 20)
            self.SubjectTextbox.resize(180, 40)
            self.SubjectTextbox.setStyleSheet(
                "padding:10px; background-color: #e6e6e6; color: rgb(0, 0, 0);  border: 2px solid #09cab8")
            self.sublayoutForm.addRow(self.SubjectLabel, self.SubjectTextbox)
            if DEBUG:
                self.SubjectTextbox.setText('Test Subject')
            elif FOR_WESTON:
                self.SubjectTextbox.setText('ViSOAR Ag Explorer Screen Shot: ')

            self.NoteLabel = QLabel('Note:')
            self.NoteTextbox = QLineEdit(self)
            self.NoteTextbox.move(20, 20)
            self.NoteTextbox.resize(180, 380)
            self.NoteTextbox.setStyleSheet(
                "padding:10px; background-color: #e6e6e6; color: rgb(0, 0, 0);  border: 2px solid #09cab8")
            self.sublayoutForm.addRow(self.NoteLabel, self.NoteTextbox)
            if DEBUG:
                self.NoteTextbox.setText('Test Note')
            elif FOR_WESTON:
                self.NoteTextbox.setText('Attached is an Image from ViSOAR Ag Explorer.')

            self.sendEmail = QPushButton('Send Email', self)
            # self.buttons.create_project.move(20,80)
            # self.create_project.resize(180,80)
            self.sendEmail.setStyleSheet(GREEN_PUSH_BUTTON)

            self.sendEmail.clicked.connect(self.emailImage)

            self.detailsBox.setLayout(self.sublayoutForm)

            self.layout.addWidget(self.InstructionsLabel)
            self.layout.addWidget(self.detailsBox)
            # self.layout.addWidget(self.buttonBox)
            self.layout.addWidget(self.sendEmail, alignment=Qt.AlignCenter)

        if DEBUG:
            print("In VisoarImageMailer 3")

        self.setLayout(self.layout)

    def emailImage( self ):
        imgWPath = self.imgWPath
        fromEmail = self.FromTextbox.text()
        toEmail = self.ToTextbox.text()
        subject = self.SubjectTextbox.text()
        note = self.NoteTextbox.text()

        gmail_user = self.FromTextbox.text()
        gmail_password = self.PasswordTextbox.text()

        # Create a secure SSL context
        context = ssl.create_default_context()

        # Create a multipart message and set headers
        message = MIMEMultipart()
        message["From"] = gmail_user
        message["To"] = toEmail
        message["Subject"] = subject
        message["Bcc"] = 'dronepilot@visus.net'  # Recommended for mass emails
        # Add body to email
        message.attach(MIMEText(note, "plain"))

        filename = self.imgWPath  # In same directory as script

        # Open PDF file in binary mode
        with open(filename, "rb") as attachment:
            # Add file as application/octet-stream
            # Email client can usually download this automatically as attachment
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())

            # Encode file in ASCII characters to send by email
            encoders.encode_base64(part)

            # Add header as key/value pair to attachment part
            part.add_header(
                "Content-Disposition",
                f"attachment; filename= {filename}",
            )

            # Add attachment to message and convert message to string
            message.attach(part)
            text = message.as_string()

            # Log in to server using secure context and send email
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
                server.login(gmail_user, gmail_password)
                server.sendmail(gmail_user, toEmail, text)

