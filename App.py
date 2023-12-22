from PyQt6.QtWidgets import QApplication, QMainWindow, QDialog, QMessageBox
from PyQt6.QtCore import Qt
from MySQLConnectionConfigure import ConnectionDialog, check_database_connection  # Replace with the actual module name
from StoreManager import MainWindow  # Replace with the actual module name


class MainApplication(QApplication):
    def __init__(self, argv):
        super().__init__(argv)

        self.connection_dialog = ConnectionDialog()

        # Loop until valid credentials are provided or the user cancels
        while True:
            result = self.connection_dialog.exec()

            if result == QDialog.DialogCode.Accepted:
                username, password, port = self.connection_dialog.get_connection_info()
                if check_database_connection(username, password, port):
                    self.connection_dialog.hide()  # or .close()
                    break  # Exit the loop if credentials are valid
                else:
                    # Show a warning message if the connection fails
                    QMessageBox.warning(None, "Warning", "Database connection failed. Please check your credentials.")
            else:
                # Exit the loop if the user cancels the connection dialog
                break

        # If you reach here, either valid credentials were provided or the user canceled
        if result == QDialog.DialogCode.Accepted:
            # Show the main store management UI
            self.main_window = MainWindow()
            self.main_window.show()


if __name__ == "__main__":
    app = MainApplication([])
    app.exec()
