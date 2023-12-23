from PyQt6.QtWidgets import QApplication, QMainWindow, QDialog, QMessageBox
from PyQt6.QtCore import Qt
from MySQLConnectionConfigure import ConnectionDialog, check_database_connection
from StoreManager import MainWindow
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)


class MainApplication(QApplication):
    def __init__(self, argv):
        super().__init__(argv)

        self.connection_dialog = ConnectionDialog()
        while True:
            result = self.connection_dialog.exec()

            if result == QDialog.DialogCode.Accepted:
                username, password, port = self.connection_dialog.get_connection_info()
                if check_database_connection(username, password, port):
                    self.connection_dialog.hide()
                    break
                else:
                    QMessageBox.warning(None, "Warning", "Database connection failed. Please check your credentials.")
            else:
                break

        if result == QDialog.DialogCode.Accepted:
            self.main_window = MainWindow()
            self.main_window.show()


if __name__ == "__main__":
    app = MainApplication([])
    app.exec()
