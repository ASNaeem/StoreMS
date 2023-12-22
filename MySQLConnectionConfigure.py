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

        # Load existing values from config.ini
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
        # Save values to config.ini upon successful connection
        self.settings.setValue("Database/user", self.userfield.text())
        self.settings.setValue("Database/password", self.passfield.text())
        self.settings.setValue("Database/port", self.portfield.text())

        super().accept()

# Function to check the database connection


def check_database_connection(username, password, port):
    try:
        # Replace 'your_host', 'your_database' with your actual database information
        connection = mysql.connector.connect(
            host='localhost',
            user=username,
            password=password,
            port=port,
            database='storedb'
        )

        # If the connection is successful, return True
        return True
    except mysql.connector.Error as err:
        # If there is an error, return False
        print(f"Error: {err}")
        return False
    finally:
        # Close the connection in the finally block to ensure it's always closed
        if 'connection' in locals():
            connection.close()


# Example of how to use the ConnectionDialog and check the connection
if __name__ == "__main__":
    app = QApplication([])

    username, password, port = "", "", ""  # Default values or values from config.ini

    # Check the database connection
    if not check_database_connection(username, password, port):
        dialog = ConnectionDialog()
        result = dialog.exec()

        if result == QDialog.DialogCode.Accepted:
            username, password, port = dialog.get_connection_info()
        else:
            # The user canceled the connection dialog, you can handle this case accordingly
            app.quit()

    # Continue with the main application using the obtained connection details
    print(f"Username: {username}, Password: {password}, Port: {port}")

    # Now you can proceed with the store management application using the obtained connection details

    app.exec()
