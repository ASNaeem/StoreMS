from PyQt6.QtWidgets import QMainWindow, QApplication, QTableWidgetItem, QMessageBox
from PyQt6.uic import loadUi
from PyQt6.QtCore import QSettings, Qt
import mysql.connector


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = QSettings("config.ini", QSettings.Format.IniFormat)
        self.username = self.settings.value("Database/user", "")
        self.password = self.settings.value("Database/password", "")
        self.port = self.settings.value("Database/port", "")

        # Load the UI file
        loadUi("StoreManager.ui", self)

        # Set up the database connection
        self.setup_database_connection()

        # Connect signals and slots
        self.pb_add_supplier.clicked.connect(self.add_supplier)
        self.pb_insert_update_product.clicked.connect(self.add_product)
        self.pb_delete_supplier.clicked.connect(self.delete_supplier)
        self.pb_delete_product.clicked.connect(self.delete_product)
        self.pb_delete_sale.clicked.connect(self.delete_sale)
        self.pb_insert_update_sale.clicked.connect(self.add_sale)
        self.pb_edit_sale.clicked.connect(self.edit_sale)
        self.pb_edit_product.clicked.connect(self.edit_product)
        self.psearch_field.textChanged.connect(self.search_products)
        self.ssearch_field.textChanged.connect(self.search_sales)
        self.sales_table.itemSelectionChanged.connect(self.cancel_edit_sale)
        self.products_table.itemSelectionChanged.connect(self.cancel_edit_product)
        # ... Add more connections and setup as needed

        # Load initial data or perform other setup tasks
        self.reload_data()

    def setup_database_connection(self):
        # Replace 'your_database_name' with your actual database name
        database_name = 'storedb'

        # Initialize the database connection
        self.conn = mysql.connector.connect(
            host='localhost',
            user=self.username,
            password=self.password,
            port=self.port,
            database=database_name
        )

        if not self.conn.is_connected():
            # print("Database connection failed.")
            self.statusbar.showMessage("Database connection failed.", 3000)
            # Handle connection failure, you might want to show an error message
        else:
            # print("Database connected successfully.")
            self.statusbar.showMessage("Database connected successfully.", 3000)

    ######################### EDIT METHODS ##############################
    def edit_sale(self):
        # Check if already in edit mode
        if self.pb_insert_update_sale.text() == "Update":
            self.cancel_edit_sale()
        else:
            # Get the selected row from the sales table
            selected_row = self.sales_table.currentRow()

            if selected_row == -1:
                # No row selected, show a message
                QMessageBox.warning(self, "Warning", "Please select a sale to edit.")
                return

            # Get the data from the selected row
            sale_id_item = self.sales_table.item(selected_row, 0)
            customer_name_item = self.sales_table.item(selected_row, 1)
            product_name_item = self.sales_table.item(selected_row, 2)
            quantity_item = self.sales_table.item(selected_row, 3)

            if None in (sale_id_item, customer_name_item, product_name_item, quantity_item):
                # Unable to retrieve sale information, show a message
                QMessageBox.warning(self, "Warning", "Unable to retrieve sale information.")
                return

            sale_id = int(sale_id_item.text())
            customer_name = customer_name_item.text()
            product_name = product_name_item.text()
            quantity = int(quantity_item.text())

            # Populate the fields with the selected data
            self.s_cnfield.setText(customer_name)
            # Assuming you have a method to get product ID based on product name
            product_id = self.get_product_id_by_name(product_name)
            self.s_pidfield.setText(str(product_id))
            self.s_pqfield.setText(str(quantity))
            self.s_sidfield.setText(str(sale_id))
            # Change the text of the insert/update button
            self.pb_insert_update_sale.setText("Update")
            self.pb_edit_sale.setText("Cancel Edit")
            self.pb_delete_sale.setEnabled(False)
            # Connect the button's click signal to the cancel edit method
            self.pb_insert_update_sale.clicked.connect(self.cancel_edit_sale)

    def cancel_edit_sale(self):
        # Reset the form and button text
        self.clear_sale()
        self.pb_insert_update_sale.setText("Insert")
        self.pb_edit_sale.setText("Edit")
        self.pb_delete_sale.setEnabled(True)
        self.statusbar.showMessage("Edit canceled, fields cleared!", 3000)

    def edit_product(self):
        # Check if already in edit mode
        if self.pb_insert_update_product.text() == "Update":
            # Reset the form and button text
            self.cancel_edit_product()
        else:
            # Get the selected row from the products table
            selected_row = self.products_table.currentRow()

            if selected_row == -1:
                # No row selected, show a message
                QMessageBox.warning(self, "Warning", "Please select a product to edit.")
                return

            # Get the data from the selected row
            product_id_item = self.products_table.item(selected_row, 0)
            product_name_item = self.products_table.item(selected_row, 1)
            price_item = self.products_table.item(selected_row, 2)
            stock_quantity_item = self.products_table.item(selected_row, 3)
            supplier_id_item = self.products_table.item(selected_row, 5)
            if None in (product_id_item, product_name_item, price_item, stock_quantity_item, supplier_id_item):
                # Unable to retrieve product information, show a message
                QMessageBox.warning(self, "Warning", "Unable to retrieve product information.")
                return

            product_id = int(product_id_item.text())
            product_name = product_name_item.text()
            price = float(price_item.text())  # Assuming price is a decimal value
            stock_quantity = int(stock_quantity_item.text())
            supplier_id = int(supplier_id_item.text())
            # Populate the fields with the selected data
            self.pidfield.setText(str(product_id))
            self.sidfield.setText(str(supplier_id))
            self.pnamefield.setText(product_name)
            self.ppricefield.setText(str(price))
            self.sqfield.setText(str(stock_quantity))
            # Change the text of the insert/update button
            self.pb_insert_update_product.setText("Update")
            self.pb_edit_product.setText("Cancel Edit")
            self.pb_delete_product.setEnabled(False)
            self.sidfield.setReadOnly(True)
            # Connect the button's click signal to the cancel edit method
            self.pb_insert_update_product.clicked.connect(self.cancel_edit_product)

    def cancel_edit_product(self):
        # Reset the form and button text
        self.clear_product()
        self.pb_insert_update_product.setText("Insert")
        self.pb_edit_product.setText("Edit")
        self.pb_delete_product.setEnabled(True)
        self.sidfield.setReadOnly(False)
        self.statusbar.showMessage("Edit canceled, fields cleared!", 3000)
    ######## UTILITY METHODS #####################

    def sorting_enable(self):
        self.sales_table.setSortingEnabled(True)
        self.products_table.setSortingEnabled(True)
        self.supplier_table.setSortingEnabled(True)

    def sorting_disable(self):
        self.sales_table.setSortingEnabled(False)
        self.products_table.setSortingEnabled(False)
        self.supplier_table.setSortingEnabled(False)

    def reload_data(self):
        self.sorting_disable()
        self.load_sales()
        self.load_products()
        self.load_suppliers()
        self.sorting_enable()

    def get_product_id_by_name(self, product_name):
        with self.conn.cursor() as cursor:
            query = "SELECT productid FROM product WHERE name = %s"
            cursor.execute(query, (product_name,))
            result = cursor.fetchone()

            if result:
                return result[0]
            else:
                QMessageBox.warning(self, "Warning", f"Product '{product_name} not found.")
                return None
    ####################### SEARCH METHODS  ###########################

    def search_products(self):
        # Implement live search for products by hiding rows
        search_text = self.psearch_field.text().lower()
        self.products_table.setSortingEnabled(False)
        for row in range(self.products_table.rowCount()):
            row_hidden = all(
                search_text not in self.products_table.item(row, col).text().lower()
                for col in range(self.products_table.columnCount())
            )
            self.products_table.setRowHidden(row, row_hidden)
        self.products_table.setSortingEnabled(True)

    def search_sales(self):
        search_text = self.ssearch_field.text().lower()
        self.sales_table.setSortingEnabled(False)
        for row in range(self.sales_table.rowCount()):
            row_hidden = all(
                search_text not in self.sales_table.item(row, col).text().lower()
                for col in range(self.sales_table.columnCount())
            )
            self.sales_table.setRowHidden(row, row_hidden)
        self.sales_table.setSortingEnabled(True)
    ####################### ADD TO DATABASE METHODS #################

    def add_supplier(self):
        # Implement logic to add a supplier to the database
        # Example:
        cursor = self.conn.cursor()
        supplier_name = self.sfield.text()

        try:
            cursor.execute("INSERT INTO supplier (name) VALUES (%s)", (supplier_name,))
            self.conn.commit()
            # print("Supplier added successfully.")
            self.statusbar.showMessage("Supplier added successfully.", 3000)
            # Reload the supplier table or perform other actions as needed
            self.sfield.clear()
            self.reload_data()
        except mysql.connector.Error as err:
            # print(f"Failed to add supplier: {err}")
            self.statusbar.showMessage(f"Failed to add supplier: {err}", 3000)
        finally:
            cursor.close()

    def add_product(self):
        # Implement logic to add or update a product in the database
        cursor = self.conn.cursor()

        product_id_text = self.pidfield.text()
        supplier_id_text = self.sidfield.text()
        product_name = self.pnamefield.text()
        price_text = self.ppricefield.text()
        stock_quantity_text = self.sqfield.text()

        # Validate that required fields are not empty
        if not product_name or not price_text or not stock_quantity_text:
            self.statusbar.showMessage("Please fill in all required fields.", 3000)
            return

        try:
            supplier_id = int(supplier_id_text)
            price = float(price_text)
            stock_quantity = int(stock_quantity_text)

            # Check if the product already exists
            if self.pb_insert_update_product.text() == "Insert":
                # Insert new product
                cursor.execute(
                    "INSERT INTO product (name, price) VALUES (%s, %s)",
                    (product_name, price)
                )
                product_id = cursor.lastrowid
                self.statusbar.showMessage("Product added successfully.", 3000)
            else:
                # Update existing product
                product_id = int(product_id_text)
                cursor.execute(
                    "UPDATE product SET name = %s, price = %s WHERE productid = %s",
                    (product_name, price, product_id)
                )
                self.statusbar.showMessage("Product updated successfully.", 3000)

            # Check if the stock entry already exists
            cursor.execute(
                "SELECT productid, supplierid FROM stock WHERE productid = %s AND supplierid = %s",
                (product_id, supplier_id)
            )
            result = cursor.fetchone()

            if result:
                # Update existing stock entry
                cursor.execute(
                    "UPDATE stock SET quantity = %s, purchasedate = CURRENT_DATE() WHERE productid = %s AND supplierid = %s",
                    (stock_quantity, product_id, supplier_id)
                )
            else:
                # Insert new stock entry
                cursor.execute(
                    "INSERT INTO stock (productid, supplierid, quantity) VALUES (%s, %s, %s)",
                    (product_id, supplier_id, stock_quantity)
                )

            self.conn.commit()
            # Reload the product table or perform other actions as needed
            self.clear_product()
            self.load_products()

        except ValueError:
            self.statusbar.showMessage("Invalid input. Please enter valid values.", 3000)
        except mysql.connector.Error as err:
            self.statusbar.showMessage(f"Failed to add/update product: {err}", 3000)
        finally:
            cursor.close()

    def add_sale(self):
        # Implement logic to add or update a sale in the database using the stored procedure
        cursor = self.conn.cursor()

        product_id_text = self.s_pidfield.text()
        customer_name = self.s_cnfield.text()
        quantity_text = self.s_pqfield.text()

        # Validate that required fields are not empty
        if not product_id_text or not customer_name or not quantity_text:
            self.statusbar.showMessage("Please fill in all required fields.", 3000)
            return

        try:
            product_id = int(product_id_text)
            quantity = int(quantity_text)

            # Check if the customer already exists
            cursor.execute("SELECT customerid FROM customer WHERE name = %s", (customer_name,))
            result = cursor.fetchone()

            if result:
                # Customer exists, get the customer ID
                customer_id = result[0]
            else:
                # Customer doesn't exist, add the customer
                cursor.execute("INSERT INTO customer (name) VALUES (%s)", (customer_name,))
                self.conn.commit()
                self.statusbar.showMessage("Customer not found, new customer added successfully.", 3000)
                # Get the customer ID of the added customer
                customer_id = cursor.lastrowid

            # Determine if it's an add or update operation based on the Insert button text
            if self.pb_insert_update_sale.text() == "Insert":
                # Call the stored procedure makepurchase for a new sale
                cursor.callproc("makepurchase", (customer_id, product_id, quantity))
                self.statusbar.showMessage("Sale added successfully.", 3000)
            elif self.pb_insert_update_sale.text() == "Update":
                # Get the selected row from the sales table
                selected_row = self.sales_table.currentRow()

                if selected_row == -1:
                    self.statusbar.showMessage("Please select a sale to update.", 3000)
                    return

                # Get the sale ID from the selected row
                sale_id_item = self.sales_table.item(selected_row, 0)
                if sale_id_item is None:
                    self.statusbar.showMessage("Unable to retrieve sale information.", 3000)
                    return

                sale_id = int(sale_id_item.text())

                # Call the stored procedure makepurchase for an update
                cursor.callproc("updatesale", (customer_id, product_id, quantity, sale_id))
                self.statusbar.showMessage("Sale updated successfully.", 3000)

            self.conn.commit()
            # Reload the sale table or perform other actions as needed
            self.clear_sale()
            self.reload_data()

        except ValueError:
            self.statusbar.showMessage("Invalid numeric input. Please enter valid numbers.", 3000)
        except mysql.connector.Error as err:
            self.statusbar.showMessage(f"Failed to add/update sale: {err}", 3000)
        finally:
            cursor.close()

    ############################# FIELD CLEAR METHODS ############################

    def clear_sale(self):
        self.s_sidfield.clear()
        self.s_cnfield.clear()
        self.s_pqfield.clear()
        self.s_pidfield.clear()

    def clear_product(self):
        self.pidfield.clear()
        self.sidfield.clear()
        self.pnamefield.clear()
        self.ppricefield.clear()
        self.sqfield.clear()
    ###################### LOAD AND POPULATE TABLE METHODS  #############

    def load_suppliers(self):
        # Implement logic to load suppliers from the database and update the UI
        # Example:
        cursor = self.conn.cursor(dictionary=True)
        cursor.execute("SELECT supplierid, name FROM supplier")
        self.supplier_table.setRowCount(0)

        for row_position, row in enumerate(cursor.fetchall()):
            self.supplier_table.insertRow(row_position)
            self.supplier_table.setItem(row_position, 0, QTableWidgetItem(str(row['supplierid'])))
            self.supplier_table.setItem(row_position, 1, QTableWidgetItem(row['name']))

        cursor.close()

    def load_products(self):
            # Clear the existing items in the table
        self.products_table.setRowCount(0)

        # Execute a query to retrieve data from the 'products' and 'stock' tables
        query = """
                SELECT p.productid, p.name, p.price, s.quantity, s.purchasedate, su.supplierid
                    FROM product p
                    JOIN stock s ON p.productid = s.productid
                    JOIN supplier su ON s.supplierid = su.supplierid
                """
        with self.conn.cursor() as cursor:
            cursor.execute(query)
            result = cursor.fetchall()
            # Populate the table with the query result
            self.products_table.setRowCount(0)
            for row_position, row_data in enumerate(result):
                self.products_table.insertRow(row_position)

                for column_position, column_value in enumerate(row_data):
                    self.products_table.setItem(row_position, column_position, QTableWidgetItem(str(column_value)))

    def load_sales(self):
        # Implement logic to load sales from the database and update the UI
        # Example:
        query = """
                    SELECT
                        saleid,
                        customer.name as customer_name,
                        product.name as product_name,
                        quantity,
                        quantity * price as total_cost,
                        saledate
                    FROM
                        sale
                    INNER JOIN
                        customer ON sale.customerid = customer.customerid
                    INNER JOIN
                        product ON sale.productid = product.productid
                """
        self.sales_table.setRowCount(0)
        with self.conn.cursor() as cursor:
            cursor.execute(query)
            result = cursor.fetchall()
            for row_position, data in enumerate(result):
                self.sales_table.insertRow(row_position)
                self.sales_table.setItem(row_position, 0, QTableWidgetItem(str(data[0])))
                self.sales_table.setItem(row_position, 1, QTableWidgetItem(data[1]))
                self.sales_table.setItem(row_position, 2, QTableWidgetItem(data[2]))
                self.sales_table.setItem(row_position, 3, QTableWidgetItem(str(data[3])))
                self.sales_table.setItem(row_position, 4, QTableWidgetItem(str(data[4])))
                self.sales_table.setItem(row_position, 5, QTableWidgetItem(str(data[5])))

    ####### DELETE METHODS  #################
    def delete_supplier(self):
        # Get the selected row from the supplier_table
        selected_row = self.supplier_table.currentRow()

        if selected_row == -1:
            # No row selected, show a message
            QMessageBox.warning(self, "Warning", "Please select a supplier to delete.")
            return

        # Get the supplier ID from the selected row
        supplier_id_item = self.supplier_table.item(selected_row, 0)
        if supplier_id_item is None:
            # Unable to retrieve supplier ID, show a message
            QMessageBox.warning(self, "Warning", "Unable to retrieve supplier information.")
            return

        supplier_id = int(supplier_id_item.text())

        # Confirm deletion with a message box
        reply = QMessageBox.question(self, "Confirmation", f"Do you want to delete supplier ID {supplier_id}?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            # Proceed with deletion
            try:
                cursor = self.conn.cursor()
                delete_query = "DELETE FROM supplier WHERE supplierid = %s"
                cursor.execute(delete_query, (supplier_id,))

                self.conn.commit()
                # print(f"Supplier ID {supplier_id} deleted successfully.")
                self.statusbar.showMessage(f"Supplier ID {supplier_id} deleted successfully.", 3000)
                # Reload the supplier table or perform other actions as needed
                self.reload_data()

            except mysql.connector.Error as err:
                # print(f"Failed to delete supplier ID {supplier_id}. Error: {err}")
                self.statusbar.showMessage(f"Failed to delete supplier ID {supplier_id}. Error: {err}", 3000)

            finally:
                cursor.close()

        else:
            # User canceled the deletion
            pass

    def delete_product(self):
        # Get the selected row from the products_table
        selected_row = self.products_table.currentRow()

        if selected_row == -1:
            # No row selected, show a message
            QMessageBox.warning(self, "Warning", "Please select a product to delete.")
            return

        # Get the product ID from the selected row
        product_id_item = self.products_table.item(selected_row, 0)
        if product_id_item is None:
            # Unable to retrieve product ID, show a message
            QMessageBox.warning(self, "Warning", "Unable to retrieve product information.")
            return

        product_id = int(product_id_item.text())

        # Confirm deletion with a message box
        reply = QMessageBox.question(self, "Confirmation", f"Do you want to delete product ID {product_id}?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            # Proceed with deletion
            cursor = self.conn.cursor()
            try:

                # Then, delete from 'product' table
                cursor.execute("DELETE FROM product WHERE productid = %s", (product_id,))
                self.conn.commit()
                # print(f"Product ID {product_id} deleted successfully.")
                self.statusbar.showMessage(f"Product ID {product_id} deleted successfully.", 3000)
                # Reload the product table or perform other actions as needed
                self.reload_data()
            except mysql.connector.Error as err:
                # print(f"Failed to delete product ID {product_id}: {err}")
                self.statusbar.showMessage(f"Failed to delete product ID {product_id}: {err}", 3000)
            finally:
                cursor.close()
        else:
            # User canceled the deletion
            pass

    def delete_sale(self):
        # Get the selected row from the sales_table
        selected_row = self.sales_table.currentRow()

        if selected_row == -1:
            # No row selected, show a message in the status bar
            self.statusbar.showMessage("Please select a sale to delete.", 3000)
            return

        # Get the sale ID from the selected row
        sale_id_item = self.sales_table.item(selected_row, 0)
        if sale_id_item is None:
            # Unable to retrieve sale ID, show a message in the status bar
            self.statusbar.showMessage("Unable to retrieve sale information.", 3000)
            return

        sale_id = int(sale_id_item.text())

        # Confirm deletion with a message box
        reply = QMessageBox.question(self, "Confirmation", f"Do you want to delete sale ID {sale_id}?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            # Proceed with deletion
            try:
                cursor = self.conn.cursor()
                cursor.execute("DELETE FROM sale WHERE saleid = %s", (sale_id,))
                self.conn.commit()
                self.statusbar.showMessage(f"Sale ID {sale_id} deleted successfully.", 3000)
                # Reload the sales table or perform other actions as needed
                self.reload_data()
            except mysql.connector.Error as err:
                self.statusbar.showMessage(f"Failed to delete sale ID {sale_id}: {err}", 3000)
            finally:
                cursor.close()
        else:
            # User canceled the deletion
            pass


# Example of how to use the MainWindow class
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
    main_window = MainWindow(username, password, port)
    main_window.show()

    app.exec()
