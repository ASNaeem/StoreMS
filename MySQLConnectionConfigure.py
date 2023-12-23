from PyQt6.QtWidgets import QApplication, QDialog, QLabel, QLineEdit, QVBoxLayout, QDialogButtonBox, QFormLayout
from PyQt6.QtCore import QSettings, Qt
from PyQt6.uic import loadUi
import mysql.connector


class ConnectionDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.settings = QSettings("config.ini", QSettings.Format.IniFormat)

        loadUi("ConnectionDialog.ui", self)

        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        self.load_config_values()

    def load_config_values(self):
        username = self.settings.value("Database/user", "")
        password = self.settings.value("Database/password", "")
        port = self.settings.value("Database/port", "")

        self.userfield.setText(username)
        self.passfield.setText(password)
        self.portfield.setText(port)

    def get_connection_info(self):
        username = self.userfield.text()
        password = self.passfield.text()
        port = self.portfield.text()
        return username, password, port

    def accept(self):
        self.settings.setValue("Database/user", self.userfield.text())
        self.settings.setValue("Database/password", self.passfield.text())
        self.settings.setValue("Database/port", self.portfield.text())

        super().accept()


def check_database_connection(username, password, port):
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user=username,
            password=password,
            port=port,
            database='storedb'
        )

        return True
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return False
    finally:
        if 'connection' in locals():
            connection.close()


if __name__ == "__main__":
    app = QApplication([])

    username, password, port = "", "", ""

    if not check_database_connection(username, password, port):
        dialog = ConnectionDialog()
        result = dialog.exec()

        if result == QDialog.DialogCode.Accepted:
            username, password, port = dialog.get_connection_info()
            app.quit()
        else:
            app.quit()

    print(f"Username: {username}, Password: {password}, Port: {port}")

    app.exec()
