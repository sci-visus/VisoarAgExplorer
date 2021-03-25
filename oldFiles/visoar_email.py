from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


from PyQt5.QtGui                      import QFont
from PyQt5.QtCore                     import QUrl, Qt, QSize, QDir, QRect
from PyQt5.QtWidgets                  import QApplication, QHBoxLayout, QLineEdit,QLabel, QLineEdit, QTextEdit, QGridLayout
from PyQt5.QtWidgets                  import QMainWindow, QPushButton, QVBoxLayout,QSplashScreen,QProxyStyle, QStyle, QAbstractButton
from PyQt5.QtWidgets                  import QWidget, QMessageBox, QGroupBox, QShortcut,QSizePolicy,QPlainTextEdit,QDialog, QFormLayout
from PyQt5.QtWebEngineWidgets         import QWebEngineView 
from PyQt5.QtWidgets                  import QTableWidget,QTableWidgetItem

from lookAndFeel                import *
from googleAutho                import *
import yagmail

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/gmail.labels']
GOOGLE_REFRESH_TOKEN ='1//0fu7G1kuCoEGlCgYIARAAGA8SNwF-L9Ir5B65_aDITdDVZX2uTK-OqbdimvYgxhsQN8LEsGu7vLnk8dPp3hi4uNG0_w4M1MRvwrg'
DEBUG = True
FOR_WESTON = False

class VisoarImageMailer(QDialog):

    def __init__(self, img, parent):
        #super().__init__()
        QDialog.__init__(self)
        if DEBUG:
            print("In VisoarImageMailer")
        self.imgWPath = img
        self.setStyleSheet(LOOK_AND_FEEL)

        # def __init__(self, *args, **kwargs):
        #     super(VMailDialog, self).__init__(*args, **kwargs)

        if DEBUG:
            print("In VMailDialog")

        #self.setWindowTitle("ViSOAR Snapshot Emailer")
        self.layout = QVBoxLayout()
        self.InstructionsLabel = QLabel('Email the ViSOAR Ag Explorer screencapture:')

        if 0:
            self.loginWithGoogle = QPushButton('Login With Google', self)
            #self.buttons.create_project.move(20,80)
            #self.create_project.resize(180,80) 
            self.loginWithGoogle.setStyleSheet(GREEN_PUSH_BUTTON)
            self.layout.addWidget(self.loginWithGoogle, alignment=Qt.AlignCenter   )
            self.loginWithGoogle.clicked.connect(  self.AOAuthorizeGmailAccount)

        

        if 1:
            self.detailsBox = QGroupBox('Email:')
            self.detailsBox.setStyleSheet(QGROUPBOX_LOOK_AND_FEEL)

   

            self.sublayoutForm = QFormLayout()

            self.FromLabel = QLabel('From:')
            self.FromTextbox = QLineEdit(self)
            if DEBUG:
                self.FromTextbox.setText('dronepilot@visus.net')
            elif FOR_WESTON:
                self.FromTextbox.setText('dronepilot@visus.net')

            self.FromTextbox.move(20, 20)
            self.FromTextbox.resize(180,40)
            self.FromTextbox.setStyleSheet("padding:10px; background-color: #e6e6e6; color: rgb(0, 0, 0);  border: 2px solid #09cab8")
            self.sublayoutForm.addRow(self.FromLabel,self.FromTextbox )

            self.ToLabel = QLabel('To:')
            self.ToTextbox = QLineEdit(self)
            self.ToTextbox.move(20, 20)
            self.ToTextbox.resize(180,40)
            self.ToTextbox.setStyleSheet("padding:10px; background-color: #e6e6e6; color: rgb(0, 0, 0);  border: 2px solid #09cab8")
            self.sublayoutForm.addRow(self.ToLabel,self.ToTextbox )
            if DEBUG:
                self.ToTextbox.setText( 'amy.a.gooch@gmail.com')
            elif FOR_WESTON:
                self.ToTextbox.setText('lramthun@gmail.com')

            self.SubjectLabel = QLabel('Subject:')
            self.SubjectTextbox = QLineEdit(self)
            self.SubjectTextbox.move(20, 20)
            self.SubjectTextbox.resize(180,40)
            self.SubjectTextbox.setStyleSheet("padding:10px; background-color: #e6e6e6; color: rgb(0, 0, 0);  border: 2px solid #09cab8")
            self.sublayoutForm.addRow(self.SubjectLabel,self.SubjectTextbox )
            if DEBUG:
                self.SubjectTextbox.setText('Test Subject')
            elif FOR_WESTON:
                self.SubjectTextbox.setText( 'ViSOAR Ag Explorer Screen Shot: ')

            self.NoteLabel = QLabel('Note:')
            self.NoteTextbox = QLineEdit(self)
            self.NoteTextbox.move(20, 20)
            self.NoteTextbox.resize(180,380)
            self.NoteTextbox.setStyleSheet("padding:10px; background-color: #e6e6e6; color: rgb(0, 0, 0);  border: 2px solid #09cab8")
            self.sublayoutForm.addRow(self.NoteLabel,self.NoteTextbox )
            if DEBUG:
                self.NoteTextbox.setText( 'Test Note')
            elif FOR_WESTON:
                self.NoteTextbox.setText( 'Attached is an Image from ViSOAR Ag Explorer.')

            self.sendEmail = QPushButton('Send Email', self)
            #self.buttons.create_project.move(20,80)
            #self.create_project.resize(180,80) 
            self.sendEmail.setStyleSheet(GREEN_PUSH_BUTTON)
            
            self.sendEmail.clicked.connect(  self.emailImage)

            self.detailsBox.setLayout(self.sublayoutForm)

            self.layout.addWidget(self.InstructionsLabel )
            self.layout.addWidget(self.detailsBox)
            #self.layout.addWidget(self.buttonBox)
            self.layout.addWidget(self.sendEmail, alignment=Qt.AlignCenter   )
 
        if DEBUG:
            print("In VisoarImageMailer 3")

        self.setLayout(self.layout)

    def AOAuthorizeGmailAccountCommandLine(self):
       # if GOOGLE_REFRESH_TOKEN is None:
        print('No refresh token found, obtaining one')
        refresh_token, access_token, expires_in = get_authorization(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET)
        print('Set the following as your GOOGLE_REFRESH_TOKEN:', refresh_token)


    def AOAuthorizeGmailAccount(self):
        """Shows basic usage of the Gmail API.
        Lists the user's Gmail labels.
        """
        if DEBUG:
            print("In AOAuthorizeGmailAccount 1")

        creds = None
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        service = build('gmail', 'v1', credentials=creds)

        # Call the Gmail API
        results = service.users().labels().list(userId='me').execute()
        labels = results.get('labels', [])

        if not labels:
            print('No labels found.')
        else:
            print('Labels:')
            for label in labels:
                print(label['name'])


    def emailImage( self ):
        imgWPath = self.imgWPath
        fromEmail = self.FromTextbox.text()
        toEmail = self.ToTextbox.text()
        subject = self.SubjectTextbox.text()
        note = self.NoteTextbox.text()
        print(fromEmail)
        try:
            yag = yagmail.SMTP(fromEmail, oauth2_file='credentials.json')
            #yag = yagmail.SMTP(fromEmail, oauth2_file='temp.json')
            contents = [
                note, "\nAttached is an Image from ViSOAR Ag Explorer",
                imgWPath, "\n", "For more information, see www.visus.net\n"
            ]
            yag.send(toEmail, subject, contents)
            self.accept()
        except:
            print("Error, email was not sent")
            self.reject()
 

# class VisoarImageMailer():
#     def __init__(self, img, parent):
#         super().__init__()
#         if DEBUG:
#             print("In VisoarImageMailer")
#         self.imgWPath = img
#         if DEBUG:
#             print("Launch Mail Dialog")
#         self.dlg = VMailDialog(self)
        

  

 