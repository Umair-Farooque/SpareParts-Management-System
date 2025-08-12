from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
import sys


class LoginWindow(QWidget):
    def __init__(self, auth, inventory, sales, printer):
        super().__init__()
        self.auth = auth
        self.inventory = inventory
        self.sales = sales
        self.printer = printer

        self.setWindowTitle("Login - Al-Hafiz Autos")
        self.setFixedSize(400, 350)
        self.setStyleSheet("""
            QWidget {
                background-color: #f5f7fa;
                font-family: 'Segoe UI';
            }
            QLabel {
                font-size: 14px;
                color: #333;
            }
            QLineEdit {
                padding: 8px;
                font-size: 14px;
                border: 1px solid #ccc;
                border-radius: 6px;
                color: #000000;
            }
            QLineEdit:focus {
                border-color: #3a7bd5;
                outline: none;
            }
            QPushButton {
                background-color: #3a7bd5;
                color: white;
                padding: 10px;
                font-weight: bold;
                border: none;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #2e5ca9;
            }
            QPushButton:pressed {
                background-color: #24497d;
            }
        """)

        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 20, 40, 20)
        layout.setSpacing(15)

        title = QLabel("Welcome to Al-Hafiz Autos Qaimpur")
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Username
        layout.addWidget(QLabel("Username:"))
        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText("Enter your username")
        layout.addWidget(self.username_edit)

        # Password
        layout.addWidget(QLabel("Password:"))
        self.password_edit = QLineEdit()
        self.password_edit.setPlaceholderText("Enter your password")
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.password_edit)
        self.password_edit.returnPressed.connect(self.login)

        # Buttons layout
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        self.login_btn = QPushButton("Login")
        self.login_btn.clicked.connect(self.login)
        btn_layout.addWidget(self.login_btn)

        self.register_btn = QPushButton("Register")
        self.register_btn.clicked.connect(self.register)
        btn_layout.addWidget(self.register_btn)

        self.reset_btn = QPushButton("Reset Password")
        self.reset_btn.clicked.connect(self.reset_pw)
        btn_layout.addWidget(self.reset_btn)

        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def login(self):
        username = self.username_edit.text().strip()
        password = self.password_edit.text()
        if self.auth.validate_login(username, password):
            self.close()
            from dashboard_window import DashboardWindow  # import here to avoid circular import
            self.dashboard = DashboardWindow(self.auth, self.inventory, self.sales, self.printer, username)
            self.dashboard.show()
        else:
            QMessageBox.critical(self, "Login Failed", "Invalid username or password.")

    def register(self):
        self._popup_form(
            title="Register New User",
            fields=[
                ("Username", False),
                ("Password", True),
                ("Security Question", False),
                ("Answer", False)
            ],
            submit_callback=self._handle_register
        )

    def reset_pw(self):
        self._popup_form(
            title="Reset Password",
            fields=[
                ("Username", False),
                ("Security Question", False),
                ("Answer", False),
                ("New Password", True)
            ],
            submit_callback=self._handle_reset_password
        )

    def _popup_form(self, title, fields, submit_callback):
        from PyQt6.QtWidgets import QDialog, QFormLayout, QLineEdit, QPushButton

        dialog = QDialog(self)
        dialog.setWindowTitle(title)
        dialog.setFixedSize(400, 350)
        dialog.setStyleSheet(self.styleSheet())

        form_layout = QFormLayout()
        entries = {}

        for label_text, is_password in fields:
            line_edit = QLineEdit()
            if is_password:
                line_edit.setEchoMode(QLineEdit.EchoMode.Password)
            entries[label_text] = line_edit
            form_layout.addRow(label_text + ":", line_edit)

        submit_btn = QPushButton("Submit")
        submit_btn.clicked.connect(lambda: self._on_form_submit(entries, submit_callback, dialog))
        form_layout.addWidget(submit_btn)

        dialog.setLayout(form_layout)
        dialog.exec()

    def _on_form_submit(self, entries, submit_callback, dialog):
        data = {label: entry.text().strip() for label, entry in entries.items()}
        if any(not val for val in data.values()):
            QMessageBox.warning(dialog, "Missing Data", "Please fill in all fields.")
            return
        if submit_callback(data, dialog):
            dialog.accept()

    def _handle_register(self, data, dialog):
        ok = self.auth.register_user(
            data["Username"], data["Password"], data["Security Question"], data["Answer"]
        )
        QMessageBox.information(dialog, "Status", "Registration successful." if ok else "User already exists.")
        return ok

    def _handle_reset_password(self, data, dialog):
        ok = self.auth.reset_password(
            data["Username"], data["Security Question"], data["Answer"], data["New Password"]
        )
        QMessageBox.information(dialog, "Status", "Password reset successfully." if ok else "Password reset failed.")
        return ok
