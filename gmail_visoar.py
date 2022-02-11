"""
Adapted from:
https://github.com/google/gmail-oauth2-tools/blob/master/python/oauth2.py
https://developers.google.com/identity/protocols/OAuth2

1. Generate and authorize an OAuth2 (generate_oauth2_token)
2. Generate a new access tokens using a refresh token(refresh_token)
3. Generate an OAuth2 string to use for login (access_token)
"""

import base64
# import imaplib
# import json

#from email.mime.image import MIMEImage
# from email.mime.multipart import MIMEMultipart
# import lxml.html
# from email import encoders
# from email.mime.base import MIMEBase
# from email.mime.multipart import MIMEMultipart
# from email.mime.text import MIMEText


#from PyQt5.QtGui                      import QFont
from PyQt5.QtCore                     import QUrl, Qt, QSize, QDir, QRect
from PyQt5.QtWidgets                  import QApplication, QHBoxLayout, QLineEdit,QLabel, QLineEdit, QTextEdit, QGridLayout
from PyQt5.QtWidgets                  import QMainWindow, QPushButton, QVBoxLayout,QSplashScreen,QProxyStyle, QStyle, QAbstractButton
from PyQt5.QtWidgets                  import QWidget, QMessageBox, QGroupBox, QShortcut,QSizePolicy,QPlainTextEdit,QDialog, QFormLayout
#from PyQt5.QtWebEngineWidgets         import QWebEngineView
#from PyQt5.QtWidgets                  import QTableWidget,QTableWidgetItem

from lookAndFeel                import *

REDIRECT_URI = ''

GOOGLE_CLIENT_ID = ''
GOOGLE_CLIENT_SECRET = ''
GOOGLE_REFRESH_TOKEN = None
#Fill in values from:
import visus_google

DEBUG = False
FOR_WESTON = True

from email.message import EmailMessage
#
# from email.mime.text import MIMEText
# from email.mime.multipart import MIMEMultipart
# from email.mime.base import MIMEBase
# from email import encoders
import logging
from io import StringIO
import smtplib
def send_email_crash_notification(crash_message, fileToAttach=None):
    email = 'dronepilot@visus.net'
    send_to_email = 'amy@visus.net'
    subject = 'ViSOAR Ag Explorer Python application CRASHED!'
    msg = EmailMessage()
    msg['From'] = email
    msg['To'] = send_to_email
    msg['Subject'] = subject
    message = crash_message
    msg.set_content( message )

    if fileToAttach:
        with open(fileToAttach, 'rb') as ap:
            import mimetypes
            mime_typeT, _ = mimetypes.guess_type(fileToAttach)
            mime_type, mime_subtype = mime_typeT.split('/', 1)
            msg.add_attachment(ap.read(), maintype=mime_type, subtype=mime_subtype,
                                filename = os.path.basename(fileToAttach))

    # Send the message via SMTP server.
    send_message_to_google(msg, email, False)
    print('email sent to ' + str(send_to_email))
    return True


class VisoarImageMailer(QDialog):

    def __init__(self, img, projName, parent, isBug=False):
        QDialog.__init__(self)
        self.isBug = isBug
        if DEBUG:
            print("In VisoarImageMailer")
        self.imgWPath = img
        self.projName = projName
        self.setStyleSheet(LOOK_AND_FEEL)
        self.refreshToken = None
        self.resize(580, 500)
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
            self.loginWithGoogle.clicked.connect(self.checkAuthorization)

        if 1:
            self.detailsBox = QGroupBox('Email:')
            self.detailsBox.setStyleSheet(QGROUPBOX_LOOK_AND_FEEL)
            self.detailsBox.resize(530, 480)
            self.sublayoutForm = QFormLayout()

            self.FromLabel = QLabel('From:')
            self.FromTextbox = QLineEdit(self)


            if DEBUG:
                self.FromTextbox.setText('dronepilot@visus.net')
            elif FOR_WESTON:
                self.FromTextbox.setText('dronepilot@visus.net')

            self.FromTextbox.move(20, 20)
            self.FromTextbox.resize(380, 40)
            self.FromTextbox.setStyleSheet(
                "padding:10px; background-color: #e6e6e6; color: rgb(0, 0, 0);  border: 2px solid #09cab8")
            self.sublayoutForm.addRow(self.FromLabel, self.FromTextbox)
            self.FromTextbox.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Preferred);
            self.FromTextbox.setMinimumWidth(380);

            self.ToLabel = QLabel('To:')
            self.ToTextbox = QLineEdit(self)
            self.ToTextbox.move(20, 20)
            self.ToTextbox.resize(380, 40)
            self.ToTextbox.setStyleSheet(
                "padding:10px; background-color: #e6e6e6; color: rgb(0, 0, 0);  border: 2px solid #09cab8")
            self.sublayoutForm.addRow(self.ToLabel, self.ToTextbox)
            if self.isBug:
                self.ToTextbox.setText('amy@visus.net')
            elif DEBUG:
                self.ToTextbox.setText('amy.a.gooch@gmail.com')
            elif FOR_WESTON:
                self.ToTextbox.setText('lance@cropsolutionsllc.com,dronepilot@visus.net')
            self.ToTextbox.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Preferred);
            self.ToTextbox.setMinimumWidth(380);

            self.SubjectLabel = QLabel('Subject:')
            self.SubjectTextbox = QLineEdit(self)
            self.SubjectTextbox.move(20, 20)
            self.SubjectTextbox.resize(380, 40)
            self.SubjectTextbox.setStyleSheet(
                "padding:10px; background-color: #e6e6e6; color: rgb(0, 0, 0);  border: 2px solid #09cab8")
            self.sublayoutForm.addRow(self.SubjectLabel, self.SubjectTextbox)
            #if DEBUG:
            if self.isBug:
                self.SubjectTextbox.setText(self.projName+' BUG REPORT: ')
            else:
                self.SubjectTextbox.setText(self.projName+': ')
            #elif FOR_WESTON:
            #    self.SubjectTextbox.setText('ViSOAR Ag Explorer Screen Shot: ')
            self.SubjectTextbox.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Preferred);
            self.SubjectTextbox.setMinimumWidth(380);

            self.NoteLabel = QLabel('Note:')
            self.NoteTextbox = QTextEdit(self)
            self.NoteTextbox.move(20, 20)

            self.NoteTextbox.setStyleSheet(
                "padding:10px; background-color: #e6e6e6; color: rgb(0, 0, 0);  border: 2px solid #09cab8")
            self.NoteTextbox.resize(380, 380)
            self.sublayoutForm.addRow(self.NoteLabel, self.NoteTextbox)
            #if DEBUG:
            #    self.NoteTextbox.setText('Test Note')
            #elif FOR_WESTON:
            if self.isBug:
                self.NoteTextbox.setText('Please edit this to tell us what you were doing and as much detail as to what it takes to repeat the bug.\n Please note you can also do a screen recoring \n\t on Windows:Win + Alt + R \n\t or use QuickTime on Mac\n\n Such recordings will have to be sent outside this app. \nOr shared with us via TeamViewer (Weston)')
            else:
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

    def launch(self):
        self.exec()

    def checkAuthorization(self):
        self.emailImage()

    def popUP(self, title, text):
        msg = QMessageBox()
        # msg = QMessageBox.about(self, title, text)
        msg.setWindowTitle(title)
        msg.setText(text)
        msg.setStyleSheet(POPUP_LOOK_AND_FEEL)
        # msg.setIcon(QMessageBox.Information)
        # msg.setStandardButtons(QMessageBox.Retry | QMessageBox.Ignore | QMessageBox.Cancel)
        # msg.setDefaultButton(QMessageBox.Ignore)
        # msg.buttonClicked.connect(self.popup_clicked)
        # if details  :
        #	msg.setDetailedText(details)
        x = msg.exec_()

    def emailImage(self):

        fromEmail = self.FromTextbox.text()
        toEmail = self.ToTextbox.text()
        subject = self.SubjectTextbox.text()
        note = self.NoteTextbox.toPlainText()

        # Create a multipart message and set headers
        message = EmailMessage()
        message["From"] = fromEmail
        message["To"] = toEmail
        message["Subject"] = subject
        message["Bcc"] = 'dronepilot@visus.net'  # Recommended for mass emails

        # Add body to email
        message.set_content( note )



        if type(self.imgWPath) == str:
            fileToAttach = self.imgWPath
            with open(fileToAttach, 'rb') as ap:
                import mimetypes
                mime_typeT, _ = mimetypes.guess_type(fileToAttach)
                mime_type, mime_subtype = mime_typeT.split('/', 1)
                message.add_attachment(ap.read(), maintype=mime_type, subtype=mime_subtype,
                                   filename=os.path.basename(fileToAttach))
        else:
            #assume it is an array
            for fileToAttach in self.imgWPath:
                with open(fileToAttach, 'rb') as ap:
                    import mimetypes
                    mime_typeT, _ = mimetypes.guess_type(fileToAttach)
                    mime_type, mime_subtype = mime_typeT.split('/', 1)
                    message.add_attachment(ap.read(), maintype=mime_type, subtype=mime_subtype,
                                           filename=os.path.basename(fileToAttach))

        #text = message.as_string()
        ret = send_message_to_google(message, fromEmail, False)
        self.close()
        popUP('Done', 'Email sent! Message ID: '+ret['id'])
        return ret

#https://stepupautomation.wordpress.com/2018/12/30/how-to-read-email-using-gmail-api-for-python/
def send_message_to_google(message, sender, exception):
    from googleapiclient.discovery import build
    from httplib2 import Http
    from oauth2client import file, client, tools

    SCOPES = 'https://www.googleapis.com/auth/gmail.send'

    #As seen in the above code, the program searches for a token.json file.
    # If the token.json file is not found, then it makes a service call based on the project credentials.json
    # file that you copied into the project folder.
    # A service object is created based on the credentials which can queried to make API calls to GMAIL.
    store = file.Storage('token.json')
    creds = store.get()
    print(os.getcwd())
    if not creds or creds.invalid:
        try:
            flow = client.flow_from_clientsecrets('client_secret_credentials.json', SCOPES)
        except Exception as e:
            print("flow: An error occurred: {}".format(e))
        try:
            creds = tools.run_flow(flow, store)
        except Exception as e:
            print("creds: An error occurred: {}".format(e))
    service = build('gmail', 'v1', http=creds.authorize(Http()))
    msg_raw = {'raw': base64.urlsafe_b64encode(message.as_string().encode()).decode()}
    try:
        message = (service.users().messages().send(userId=sender, body=msg_raw).execute())
        print("Message Id: {}".format(message['id']))
        return message
    except Exception as e:
        print("An error occurred: {}".format(e))
        #try to move token.json and rerun this function
        if not exception:
            import shutil
            shutil.move('token.json', 'token.json.bk')
            send_message_to_google(message, sender, True)
        raise e