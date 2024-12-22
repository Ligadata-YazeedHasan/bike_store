import os, re

from PyQt6.QtWidgets import QWidget, QGridLayout, \
    QLabel, QMainWindow, QMessageBox, QLineEdit, QPushButton, QCheckBox
from PyQt6.QtGui import QIcon, QAction

from controllers.controller import MainApp
from models.models import User
from utilities.utils import remember_me, get_me
from common.consts import GENERAL_QLabel_STYLESHEET, GENERAL_QLineEdit_STYLESHEET, UNHIDDEN_EYE_ICON_PATH, \
    SMALLER_QLabel_STYLESHEET, GENERAL_QPushButton_STYLESHEET, HIDDEN_EYE_ICON_PATH, APP_NAME, LOGIN_SCREEN_HEIGHT, \
    LOGIN_SCREEN_WIDTH, FORGET_PASSWORD_SCREEN_HEIGHT, FORGET_PASSWORD_WIDTH, MAIN_SCREEN_HEIGHT, \
    MAIN_SCREEN_LEFT_CORNER_START, MAIN_SCREEN_TOP_CORNER_START, REMEMBER_LAST_ACTIVE_FILE_PATH, REMEMBER_ME_FILE_PATH
from views.custome import QClickableLabel


class LoginForm(QWidget):
    def __init__(self, state=None):
        super(LoginForm, self).__init__()
        self.__init_ui()
        self.screen = None
        layout = QGridLayout()

        label_name = QLabel('Email')
        label_name.setStyleSheet(GENERAL_QLabel_STYLESHEET)
        self.lineEdit_username = QLineEdit()
        self.lineEdit_username.setStyleSheet(GENERAL_QLineEdit_STYLESHEET)
        self.lineEdit_username.setPlaceholderText('Please enter your email...')
        layout.addWidget(label_name, 0, 0)
        layout.addWidget(self.lineEdit_username, 0, 1, 1, 3, )

        label_password = QLabel('Password')
        label_password.setStyleSheet(GENERAL_QLabel_STYLESHEET)
        self.lineEdit_password = QLineEdit()

        self.lineEdit_password.setStyleSheet(GENERAL_QLineEdit_STYLESHEET)
        self.lineEdit_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.lineEdit_password.setPlaceholderText('Please enter your password...')

        self.__show_pass_action = QAction(QIcon(UNHIDDEN_EYE_ICON_PATH), 'Show password', self)
        self.__show_pass_action.setCheckable(True)
        self.__show_pass_action.toggled.connect(self.show_password)
        self.lineEdit_password.addAction(self.__show_pass_action, QLineEdit.ActionPosition.TrailingPosition)

        layout.addWidget(label_password, 1, 0)
        layout.addWidget(self.lineEdit_password, 1, 1, 1, 3, )

        self.remember_me = QCheckBox('Remember me')
        self.remember_me.setStyleSheet(SMALLER_QLabel_STYLESHEET)
        layout.addWidget(self.remember_me, 2, 0)

        label_forget_password = QClickableLabel('Forget Password?', self.forget_password, )
        label_forget_password.setStyleSheet(SMALLER_QLabel_STYLESHEET)
        layout.addWidget(label_forget_password, 2, 3)

        button_login = QPushButton('Login')
        button_login.setStyleSheet(GENERAL_QPushButton_STYLESHEET)
        button_login.clicked.connect(self.check_password)
        layout.addWidget(button_login, 3, 0, 1, 4, )

        layout.setRowMinimumHeight(2, 150)
        layout.setContentsMargins(15, 25, 15, 25)
        self.setLayout(layout)

        if state is None:
            self.__try_remember_me_login()

    def show_password(self, ):
        if self.lineEdit_password.echoMode() == QLineEdit.EchoMode.Normal:
            self.lineEdit_password.setEchoMode(QLineEdit.EchoMode.Password)
            self.__show_pass_action.setIcon(QIcon(UNHIDDEN_EYE_ICON_PATH))
        else:
            self.lineEdit_password.setEchoMode(QLineEdit.EchoMode.Normal)
            self.__show_pass_action.setIcon(QIcon(HIDDEN_EYE_ICON_PATH))

    def __init_ui(self):
        self.setWindowTitle(APP_NAME + ' -- Login Form')
        height = LOGIN_SCREEN_HEIGHT
        width = LOGIN_SCREEN_WIDTH
        self.resize(width, height)
        self.setMinimumHeight(height)
        self.setMaximumHeight(height)

        self.setMinimumWidth(width)
        self.setMaximumWidth(width)

        pass

    def check_password(self):
        msg = QMessageBox()
        email = self.lineEdit_username.text().lower()
        password = self.lineEdit_password.text()
        if email is None or not email:
            msg.setText('Please enter an email.')
            msg.exec()
            return

        if password is None or not password:
            msg.setText('Please enter a password.')
            msg.exec()
            return

        # if password.isalnum():
        #     msg.setText('Please enter a password.')
        #     msg.exec()
        #     return

        regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        if not re.fullmatch(regex, email):
            msg.setText('Email must be in an email format.')
            msg.exec()
            return
        user = self.__load_user_data(email, password)
        if self.remember_me.isChecked():
            remember_me({
                'email': user.email,
                'password': user.password,
            },
                REMEMBER_ME_FILE_PATH
            )
        if user:
            self.next_screen(user)

    def forget_password(self, event):
        self.screen = ForgetPasswordForm()
        self.screen.show()
        self.hide()
        self.destroy()
        self.close()

    def __load_user_data(self, email, password):
        msg = QMessageBox()
        user = MainApp.DB_FACTORY.session.query(User).filter(User.email == email).first()
        if user:
            return user
        else:
            msg.setText("User is not found.")
            msg.exec()
            return False

    def __try_remember_me_login(self, ):
        msg = QMessageBox()
        data = get_me(REMEMBER_ME_FILE_PATH)

        if data:
            user = self.__load_user_data(
                email=data['email'],
                password=data['password'],
            )
        else:
            msg.setText("Could not load pre-saved user.")
            msg.exec()
            return

        # remember_me({
        #     'email': user.email,
        #     'password': user.password,
        # }, REMEMBER_ME_FILE_PATH)
        self.next_screen(user)
    #     return True

    def next_screen(self, user):
        self.screen = MainForm(
            user=user,
        )
        self.screen.show()

        self.hide()
        self.destroy()
        self.close()

        pass


class ForgetPasswordForm(QWidget):
    """ This "window" is a QWidget. If it has no parent, it will appear as a free-floating window as we want.
    """

    def __init__(self, ):
        super(ForgetPasswordForm, self).__init__()
        self.__init_ui()

        layout = QGridLayout()

        label_name = QLabel('Email')
        label_name.setStyleSheet(GENERAL_QLabel_STYLESHEET)
        layout.addWidget(label_name, 0, 0)

        self.lineEdit_username = QLineEdit()
        self.lineEdit_username.setStyleSheet(GENERAL_QLineEdit_STYLESHEET)
        self.lineEdit_username.setPlaceholderText('Please enter your email...')
        layout.addWidget(self.lineEdit_username, 0, 1, )

        button_check = QPushButton('Check')
        button_check.adjustSize()
        button_check.setStyleSheet(GENERAL_QPushButton_STYLESHEET)

        button_check.clicked.connect(self.check_email)
        layout.addWidget(button_check, 1, 1, )

        button_back = QPushButton('Back')
        button_back.adjustSize()
        button_back.setStyleSheet(GENERAL_QPushButton_STYLESHEET)
        button_back.clicked.connect(self.return_to_login_page)
        layout.addWidget(button_back, 1, 0, 1, 1)

        # layout.setRowMinimumHeight(10, 75)
        layout.setContentsMargins(10, 0, 10, 0)
        self.setLayout(layout)

    def __init_ui(self):
        self.setWindowTitle(APP_NAME + ' -- Forget Password Form')
        height = FORGET_PASSWORD_SCREEN_HEIGHT
        width = FORGET_PASSWORD_WIDTH
        self.resize(width, height)
        self.setMinimumHeight(height)
        self.setMaximumHeight(height)

        self.setMinimumWidth(width)
        self.setMaximumWidth(width)

        pass

    def check_email(self):
        msg = QMessageBox()
        email = self.lineEdit_username.text().lower()
        if email is None or email == '':
            msg.setText('Please enter an email to validate.')
            msg.exec()
            return

        regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        if not re.fullmatch(regex, email):
            msg.setText('Text must be in an email format.')
            msg.exec()
            return

        res = MainApp.DB_FACTORY.session.query(User).filter(User.email == email).first()
        if res:
            msg.setText('You will receive an email with the details.')
            self._send_email(res)
        else:
            msg.setText("Could not find this user in the system.")
        msg.exec()
        return

    def return_to_login_page(self):
        LoginForm(state='reverse').show()
        self.hide()
        self.destroy()
        self.close()
        pass

    def _send_email(self, res):
        MainApp.MAILER.send_email(
            subject="Test Email, For Fun",
            body="Hi, How are you",
            receivers=[res.email],
            # receivers=['sondosalqaisi323@gmail.com'],
            attachments=None,
            inline_attachments=None
        )

        pass


class MainForm(QMainWindow):
    def __init__(self, user=None):
        super(MainForm, self).__init__()

        self.__init_ui()

        self.user = user


    def __logout(self):
        if os.path.exists(REMEMBER_ME_FILE_PATH):
            os.remove(REMEMBER_ME_FILE_PATH)

        if os.path.exists(REMEMBER_LAST_ACTIVE_FILE_PATH):
            os.remove(REMEMBER_LAST_ACTIVE_FILE_PATH)

        LoginForm(state='reverse').show()
        self.hide()
        self.destroy()
        self.close()

    def __init_ui(self, ):
        self.setWindowTitle(APP_NAME)
        width = int(MAIN_SCREEN_HEIGHT * 1.61)
        self.setGeometry(
            MAIN_SCREEN_LEFT_CORNER_START,
            MAIN_SCREEN_TOP_CORNER_START,
            width,
            MAIN_SCREEN_HEIGHT,
        )

        self.setMinimumHeight(MAIN_SCREEN_HEIGHT)
        self.setMaximumHeight(MAIN_SCREEN_HEIGHT)

        self.setMinimumWidth(width)
        self.setMaximumWidth(width)
        # self.setWindowIcon(QIcon('logo.png'))

    def __init_layouts(self):
        pass
