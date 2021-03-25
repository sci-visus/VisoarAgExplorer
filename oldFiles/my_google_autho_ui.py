"""
Adapted from:
https://blog.macuyiko.com/post/2016/how-to-send-html-mails-with-oauth2-and-gmail-in-python.html

https://github.com/google/gmail-oauth2-tools/blob/master/python/oauth2.py
https://developers.google.com/identity/protocols/OAuth2

1. Generate and authorize an OAuth2 (generate_oauth2_token)
2. Generate a new access tokens using a refresh token(refresh_token)
3. Generate an OAuth2 string to use for login (access_token)
"""

import base64
import imaplib
import json
import smtplib
import urllib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import lxml.html

GOOGLE_ACCOUNTS_BASE_URL = 'https://accounts.google.com'
REDIRECT_URI = 'urn:ietf:wg:oauth:2.0:oob'

GOOGLE_CLIENT_ID = '1049418758773-uquddk7b9gag6i7pfsouio3c5mj3dl8l.apps.googleusercontent.com'
GOOGLE_CLIENT_SECRET = 'BV_7TAFIP8VQiETt5LCgKgIx'
GOOGLE_REFRESH_TOKEN = None

"""Auth module that uses a QT or GTK browser to prompt the user."""
import signal
from contextlib import contextmanager


from PyQt5.QtGui                      import QFont
from PyQt5.QtCore                     import QUrl, Qt, QSize, QDir, QRect
from PyQt5.QtWidgets                  import QApplication, QHBoxLayout, QLineEdit,QLabel, QLineEdit, QTextEdit, QGridLayout
from PyQt5.QtWidgets                  import QMainWindow, QPushButton, QVBoxLayout,QSplashScreen,QProxyStyle, QStyle, QAbstractButton
from PyQt5.QtWidgets                  import QWidget, QMessageBox, QGroupBox, QShortcut,QSizePolicy,QPlainTextEdit,QDialog, QFormLayout
from PyQt5.QtWebEngineWidgets         import QWebEngineView
from PyQt5.QtWidgets                  import QTableWidget,QTableWidgetItem
from PyQt5.QtWebEngineWidgets         import QWebEngineView ,QWebEnginePage
from PyQt5.QtWebEngineWidgets import QWebEngineSettings as QWebSettings

from lookAndFeel                import *

CHECK_AUTH_JS = """
    var code = document.getElementById("code");
    var access_denied = document.getElementById("access_denied");
    var result;

    if (code) {
        result = {authorized: true, code: code.value};
    } else if (access_denied) {
        result = {authorized: false, message: access_denied.innerText};
    } else {
        result = {};
    }
    result;
"""


class VisusGoogleWebAutho(QDialog):

    def __init__(self, parent):
        # super().__init__()
        QDialog.__init__(self)
        #self.visusGoogleAuth = VisusGoogleAutho()
        #self.visusGoogleAuth.authorization_code = ''
        self.parent =parent
        title = 'Authorize Email'
        size = (400, 700)
        self.setWindowTitle(title)
        self.resize(*size)
        self.setStyleSheet(LOOK_AND_FEEL)

        self.webview = QWebEngineView()
        self.webpage = QWebEnginePage()
        self.webview.setPage(self.webpage)
        self.webpage.loadFinished.connect(lambda: self._on_qt_page_load_finished())

        self.backToVisoarBtn = QPushButton('Take Code back to ViSOAR', self)
        self.backToVisoarBtn.setStyleSheet(GREEN_PUSH_BUTTON)
        self.backToVisoarBtn.clicked.connect(self.goBackToVisoar)

        # self.pasteFromGoogleBtn = QPushButton('Take Code back to ViSOAR', self)
        # self.pasteFromGoogleBtn.setStyleSheet(GREEN_PUSH_BUTTON)
        # self.pasteFromGoogleBtn.clicked.connect(self.pasteFromGoogle)


        self.labelInstructions = QLabel(
            'When you get to the page to copy the code, and place it in the text box below.  Then  press this button to go back to the ViSOAR App with the Verification Code')
        self.codeTextbox = QLineEdit(self)
        self.codeTextbox.move(20, 20)
        self.codeTextbox.resize(180, 40)
        self.codeTextbox.setStyleSheet(
            "padding:10px; background-color: #e6e6e6; color: rgb(0, 0, 0);  border: 2px solid #09cab8")

        layout = QGridLayout()
        layout.addWidget(self.webview)
        layout.addWidget(self.labelInstructions)#, alignment=Qt.AlignLeft)
        layout.addWidget(self.codeTextbox)  # , alignment=Qt.AlignCenter)
        #layout.addWidget(self.pasteFromGoogleBtn)  # , alignment=Qt.AlignCenter)
        layout.addWidget(self.backToVisoarBtn)#, alignment=Qt.AlignCenter)

        self.setLayout(layout)
        self.authorization_code = None

        #self.get_authorization(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET)
        scope = "https://mail.google.com/"
        self.url = self.generate_permission_url(GOOGLE_CLIENT_ID, scope)
        print(self.url)
        # gmailURL = urllib.quote(url)
        # print(gmailURL)
        # self.authorization_code = self.get_code(self.url)
        # self.authorization_code = self.get_code(self.url)
        self.webpage.load(QUrl(self.url))
        self.webview.show()

    # def pasteFromGoogle(self):
    #     import pyperclip
    #     pyperclip.paste()

    def command_to_url(self, command):
        return '%s/%s' % (GOOGLE_ACCOUNTS_BASE_URL, command)

    def url_escape(self, text):
        return urllib.parse.quote(text, safe='~-._')

    def url_unescape(self, text):
        return urllib.parse.unquote(text)

    def url_format_params(self, params):
        param_fragments = []
        for param in sorted(params.items(), key=lambda x: x[0]):
            param_fragments.append('%s=%s' % (param[0], self.url_escape(param[1])))
        print('&'.join(param_fragments))
        return '&'.join(param_fragments)

    def generate_permission_url(self, client_id, scope='https://mail.google.com/'):
        params = {}
        params['client_id'] = client_id
        params['redirect_uri'] = REDIRECT_URI
        params['scope'] = scope
        params['response_type'] = 'code'
        print('%s?%s' % (self.command_to_url('o/oauth2/auth'), self.url_format_params(params)))
        return '%s?%s' % (self.command_to_url('o/oauth2/auth'), self.url_format_params(params))

    def call_authorize_tokens(self, client_id, client_secret, authorization_code):
        params = {}
        params['client_id'] = client_id
        params['client_secret'] = client_secret
        params['code'] = authorization_code
        params['redirect_uri'] = REDIRECT_URI
        params['grant_type'] = 'authorization_code'
        request_url = self.command_to_url('o/oauth2/token')
        response = urllib.request.urlopen(request_url, urllib.parse.urlencode(params).encode('UTF-8')).read().decode(
            'UTF-8')
        print(response)
        return json.loads(response)

    def call_refresh_token(self, client_id, client_secret, refresh_token):
        params = {}
        params['client_id'] = client_id
        params['client_secret'] = client_secret
        params['refresh_token'] = refresh_token
        params['grant_type'] = 'refresh_token'
        request_url = self.command_to_url('o/oauth2/token')
        #request_url = "https://accounts.google.com/o/oauth2/token?client_id="+client_id+"&client_secret="+client_secret+"&refresh_token="+refresh_token+"&grant_type=refresh_token"
        response = urllib.request.urlopen(request_url, urllib.parse.urlencode(params).encode('UTF-8')).read().decode( 'UTF-8')
        #response = urllib.request.urlopen(request_url).read().decode( 'UTF-8')

        #print(request_url)
        #ret = urllib.request.urlopen(request_url).read().decode( 'UTF-8')
        return json.loads(response)
        #return json.loads(ret)

    def generate_oauth2_string(self, username, access_token, as_base64=False):
        auth_string = 'user=%s\1auth=Bearer %s\1\1' % (username, access_token)
        if as_base64:
            auth_string = base64.b64encode(auth_string.encode('ascii')).decode('ascii')
        return auth_string

    def test_imap(self, user, auth_string):
        imap_conn = imaplib.IMAP4_SSL('imap.gmail.com')
        imap_conn.debug = 4
        imap_conn.authenticate('XOAUTH2', lambda x: auth_string)
        imap_conn.select('INBOX')

    def test_smpt(self, user, base64_auth_string):
        smtp_conn = smtplib.SMTP('smtp.gmail.com', 587)
        smtp_conn.set_debuglevel(True)
        smtp_conn.ehlo('test')
        smtp_conn.starttls()
        smtp_conn.docmd('AUTH', 'XOAUTH2 ' + base64_auth_string)

    def get_authorization(self, google_client_id, google_client_secret):
        scope = "https://mail.google.com/"
        #self.authorization_code = ''
        try:
            self.url = self.generate_permission_url(google_client_id, scope)
            print(self.url)
            # gmailURL = urllib.quote(url)
            # print(gmailURL)
            #self.authorization_code = self.get_code(self.url)
            #self.authorization_code = self.get_code(self.url)
            self.webpage.load(QUrl(self.url))
            self.webview.show()

        except:
            print('ERROR in gettin authorization code from gmail')

    def myUseAuthorizationCode(self):
        print(self.authorization_code)

        # print('Navigate to the following URL to auth:', self.generate_permission_url(google_client_id, scope))
        # authorization_code = input('Enter verification code: ')
        response = self.call_authorize_tokens(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, self.authorization_code)
        return response['refresh_token'], response['access_token'], response['expires_in']

    def refresh_authorization(self, google_client_id, google_client_secret, refresh_token):
        response = self.call_refresh_token(google_client_id, google_client_secret, refresh_token)
        return response['access_token'], response['expires_in']

    def refresh_authorizationbroke(self, google_client_id, google_client_secret, refresh_token):
        self.refreshToken(google_client_id, google_client_secret, refresh_token)
        #return response['access_token'], response['expires_in']

        # {"email_address": "amy@visus.net",
        # "google_client_id":  google_client_id,
        ##  "google_client_secret": google_client_secret,
        #  "google_refresh_token": refresh_token}

        # Call refreshToken which creates a new Access Token
        #access_token = refreshToken(client_id, client_secret, refresh_token)

        # // Pass the new Access Token to Credentials() to create new credentials
        #credentials = google.oauth2.credentials.Credentials(access_token)

    # // This function creates a new Access Token using the Refresh Token
    # // and also refreshes the ID Token (see comment below).
    def saveToken(self, google_client_id, google_client_secret, refresh_token):

        data =  {"email_address": "amy@visus.net",
                "google_client_id": google_client_id,
                "google_client_secret": google_client_secret,
                "google_refresh_token": refresh_token}

        with open('credentials.json', 'w') as outfile:
            json.dump(data, outfile)

    def getUrl(self):

        return self.url



    @contextmanager
    def default_sigint(self):
        """Context manager that sets SIGNINT to the default value."""
        original_sigint_handler = signal.getsignal(signal.SIGINT)
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        try:
            yield
        finally:
            signal.signal(signal.SIGINT, original_sigint_handler)

        WEBKIT_BACKEND = "qt"


    def _on_qt_page_load_finished(self):
        #self.get_authorization(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET)
        res = self.webpage.runJavaScript("document.getElementsByTagName('textarea')[0].innerhtml")
        #authorization = dict((k, v) for (k, v) in res.items())
        #if "authorized" in authorization:
        #    self.authorization_code = authorization.get("code")
        #    self.close()
        #self.authorization_code = res
        #self.refresh()
        #self.close()
        return res

    def getAuthorizationCode(self):
        return  self.authorization_code

    def setAuthorizationCode(self):
        self.authorization_code = self.codeTextbox.text() #self.webpage.runJavaScript("document.getElementsByTagName('textarea')[0].innerhtml")

    def refresh(self, refreshToken):
        return (self.refresh_authorization(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, refreshToken))

    def showDialog(self):
        self.show()
        self.webview.show()

    def hideDialog(self ):
        self.hide()
        self.webview.hide()


    def goBackToVisoar(self):
        self.setAuthorizationCode()
        print(self.authorization_code)
        print('Launching Visoar Email: '+self.authorization_code)
        #self.parent.emailImageWithCode(self.authorization_code)
        self.saveToken(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET,self.authorization_code)
        self.parent.emailImage()

    #https://github.com/tokland/shoogle/blob/master/shoogle/auth/browser.py
    def get_code(self, url, size=(640, 480), title="Google authentication"):
        """Open a QT webkit window and return the access code."""
        print(url)
        # self.webview.setUrl(QUrl(url))

        self.webpage.load(QUrl(url))

        return self.authorization_code