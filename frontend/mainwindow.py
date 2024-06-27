from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QPlainTextEdit, QPushButton, \
    QTableWidget, QTableWidgetItem, QFileDialog, QToolTip, QAction, QTextBrowser, QDialog, QComboBox, QToolBar, \
    QCompleter, QProgressDialog, QMessageBox, QAbstractItemView, QTextEdit
from PyQt5.QtCore import Qt, pyqtSlot, QThread, pyqtSignal, QSize, QRect, QRegExp
from PyQt5.QtGui import QTextCursor, QTextCharFormat, QColor, QIcon, QPainter, QTextFormat, QFont, QSyntaxHighlighter
import sys
import os
import sqlite3
import datetime


class AllCapsHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.allCapsFormat = QTextCharFormat()
        self.allCapsFormat.setForeground(QColor("#FFF500"))

        self.specialCharFormat = QTextCharFormat()
        self.specialCharFormat.setForeground(QColor("magenta"))

        # Define the regular expressions for patterns
        self.allCapsPattern = QRegExp(r'\b[A-Z]+\b')
        self.specialCharPattern = QRegExp(r'\W')

    def highlightBlock(self, text):
        # Highlight all caps words
        index = self.allCapsPattern.indexIn(text)
        while index >= 0:
            length = self.allCapsPattern.matchedLength()
            self.setFormat(index, length, self.allCapsFormat)
            index = self.allCapsPattern.indexIn(text, index + length)

        # Highlight special characters
        index = self.specialCharPattern.indexIn(text)
        while index >= 0:
            length = self.specialCharPattern.matchedLength()
            self.setFormat(index, length, self.specialCharFormat)
            index = self.specialCharPattern.indexIn(text, index + length)

class LineNumberArea(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.codeEditor = editor

    def sizeHint(self):
        return QSize(self.editor.lineNumberAreaWidth(), 0)

    def paintEvent(self, event):
        self.codeEditor.lineNumberAreaPaintEvent(event)


class CodeEditor(QPlainTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.lineNumberArea = LineNumberArea(self)
        self.lineNumberAreaFont = QFont("Courier New", 9, QFont.Bold)
        self.lineNumberAreaBgColor = QColor("#222")
        self.lineNumberAreaTextColor = QColor("#FFF")
        self.blockCountChanged.connect(self.updateLineNumberAreaWidth)
        self.updateRequest.connect(self.updateLineNumberArea)
        self.cursorPositionChanged.connect(self.highlightCurrentLine)
        self.updateLineNumberAreaWidth(0)

        # Initialize the syntax highlighter
        self.highlighter = AllCapsHighlighter(self.document())

    def lineNumberAreaWidth(self):
        digits = self.blockCount()
        max_digits = len(str(max(1, digits)))
        charWidth = self.fontMetrics().boundingRect('9').width()
        space = charWidth * max_digits + 15
        return space

    def updateLineNumberAreaWidth(self, _):
        self.setViewportMargins(self.lineNumberAreaWidth(), 0, 0, 0)

    def updateLineNumberArea(self, rect, dy):
        if dy:
            self.lineNumberArea.scroll(0, dy)
        else:
            self.lineNumberArea.update(0, rect.y(), self.lineNumberArea.width(), rect.height())

        if rect.contains(self.viewport().rect()):
            self.updateLineNumberAreaWidth(0)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.lineNumberArea.setGeometry(QRect(cr.left(), cr.top(), self.lineNumberAreaWidth(), cr.height()))

    def lineNumberAreaPaintEvent(self, event):
        painter = QPainter(self.lineNumberArea)
        painter.fillRect(event.rect(), self.lineNumberAreaBgColor)

        block = self.firstVisibleBlock()
        blockNumber = block.blockNumber()
        top = self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
        bottom = top + self.blockBoundingRect(block).height()

        painter.setFont(self.lineNumberAreaFont)

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                painter.setPen(self.lineNumberAreaTextColor)
                painter.drawText(0, int(top), self.lineNumberArea.width(), self.fontMetrics().height(),
                                 Qt.AlignRight, str(blockNumber + 1))

            block = block.next()
            top = bottom
            bottom = top + self.blockBoundingRect(block).height()
            blockNumber += 1

    def highlightCurrentLine(self):
        extraSelections = []
        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()
            lineColor = QColor(Qt.white).lighter(7)
            selection.format.setBackground(lineColor)
            selection.format.setProperty(QTextFormat.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extraSelections.append(selection)
        self.setExtraSelections(extraSelections)

class TextPopup(QDialog):
    def __init__(self, content, parent=None):
        super().__init__(parent)
        self.setWindowTitle('SQL Query Bank') 
        self.setGeometry(300, 300, 700, 400)

        layout = QVBoxLayout()

        self.textBrowser = QTextBrowser()
        self.textBrowser.setStyleSheet("background-color: black; color: white; font-size: 10pt; font-family: Courier;")
        self.highlightSyntax(content)

        layout.addWidget(self.textBrowser)
        self.setLayout(layout)

    def highlightSyntax(self, content):
        # Prepare format for syntax highlighting
        format = QTextCharFormat()
        format.setForeground(QColor('red'))

        # Split content into lines
        lines = content.splitlines()

        # Prepare a cursor to manipulate the text
        cursor = QTextCursor(self.textBrowser.document())

        # Clear any previous formatting
        cursor.select(QTextCursor.Document)
        cursor.setCharFormat(QTextCharFormat())

        # Iterate through each line and apply formatting if it starts with "--"
        formatted_content = ""
        for line in lines:
            if line.strip().startswith("--"):
                cursor.insertHtml(f"<span style='color:red;'>{line}</span><br>")
            else:
                cursor.insertText(line + "\n")

        # Set the cursor back to the start and update the text browser
        cursor.setPosition(0)
        self.textBrowser.setTextCursor(cursor)

class BankSQLWorker(QThread):
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, path):
        super().__init__()
        self.path = path

    def run(self):
        try:
            with open(self.path, 'r') as file:
                content = file.read()
            self.finished.emit(content)
        except Exception as e:
            self.error.emit(str(e))

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('ZenSQL - Editor')
        self.setGeometry(0, 0, 800, 800)
        self.setStyleSheet("background-color: black; color: white;")

        self.db_path = None
        self.conn = None
        self.cursor = None

        self.initUI()

    def initUI(self):
        centralWidget = QWidget(self)
        self.setCentralWidget(centralWidget)

        layout = QVBoxLayout()

        # Create a QToolBar for actions and table selection
        toolbar = QToolBar("Main Toolbar")
        self.addToolBar(toolbar)

        # Add a menu item for "Database"
        menubar = self.menuBar()
        menubar.setStyleSheet("""
            QMenuBar {
                background-color: #000;
                color: white;
                padding: 5px;
                border: 1px solid grey;
            }
            QMenuBar::item {
                padding: 5px 10px;
                background-color: transparent;
                border: 1px solid grey;
            }
            QMenuBar::item:selected {
                background-color: #333;
            }
            QMenu {
                background-color: #333;
                color: white;
                border: 1px solid grey;
            }
            QMenu::item {
                padding: 5px 20px;
            }
            QMenu::item:selected {
                background-color: #555;
            }
        """)
        db_menu = menubar.addMenu('&Database')

        # Load Database Action (Moved from button to menu)
        load_action = QAction('Load .db File', self)
        load_action.triggered.connect(self.load_database)
        db_menu.addAction(load_action)

        # Generate Database Action (Moved from button to menu)
        gen_action = QAction('Generate Database', self)
        gen_action.triggered.connect(self.generate_database)
        db_menu.addAction(gen_action)

        # Add a button for "Bank SQL"
        bank_action = QAction('Query Bank', self)
        bank_action.triggered.connect(self.open_bank_sql)
        toolbar.addAction(bank_action)
        toolbar.addSeparator()

        # Style the toolbar buttons
        toolbar.setStyleSheet("""
            QToolButton {
                padding: 5px;
                border: 1px solid grey;
            }
            QToolButton:hover {
                background-color: #333;
            }
        """)

        # Table Dropdown Menu in Toolbar
        self.tableLabel = QLabel("Current Table:")
        self.tableLabel.setStyleSheet("margin-right: 10px; color: white;")
        toolbar.addWidget(self.tableLabel)

        self.tableComboBox = QComboBox()
        self.tableComboBox.setToolTip("Select a table to view its data.")
        self.tableComboBox.currentIndexChanged.connect(self.load_table_data)
        toolbar.addWidget(self.tableComboBox)

        self.queryInput = CodeEditor()
        self.queryInput.setPlaceholderText("Enter SQL query here...")
        self.queryInput.setStyleSheet("background-color: #000; color: limegreen;")
        layout.addWidget(self.queryInput, stretch=1)

        # Execute Query Button
        executeButton = QPushButton("Execute Query")
        executeButton.setStyleSheet("""
            QPushButton {
                padding: 5px;
                border: 1px solid grey;
            }
            QPushButton:hover {
                background-color: #333;
            }
        """)
        executeButton.clicked.connect(self.execute_query)
        layout.addWidget(executeButton)

        # Database Header Information Button
        self.headerInfoButton = QPushButton("Table Header Info")
        self.headerInfoButton.setStyleSheet("""
            QPushButton {
                padding: 5px;
                border: 1px solid grey;
            }
            QPushButton:hover {
                background-color: #333;
            }
        """)
        self.headerInfoButton.setToolTip("Click this button to see database header information.")
        self.headerInfoButton.setCheckable(True)
        self.headerInfoButton.toggled.connect(self.toggle_header_info)
        layout.addWidget(self.headerInfoButton)

        # Table Display (Two-Thirds)
        self.resultTable = QTableWidget()
        self.resultTable.setStyleSheet("background-color: #111; color: white; font-family: Courier;")  # Example styling
        self.resultTable.setEditTriggers(QAbstractItemView.DoubleClicked | QAbstractItemView.EditKeyPressed)
        layout.addWidget(self.resultTable, stretch=4)

        # Status Label
        self.statusLabel = QLabel()
        layout.addWidget(self.statusLabel)

        centralWidget.setLayout(layout)

    @pyqtSlot()
    def load_database(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(self, "Load Database File", "", "SQLite Database Files (*.db);;All Files (*)", options=options)
        if fileName:
            self.connect_to_database(fileName)
            self.load_tables()

    def connect_to_database(self, db_path):
        try:
            if self.conn:
                self.conn.close()
            self.conn = sqlite3.connect(db_path)
            self.cursor = self.conn.cursor()
            self.db_path = db_path

            # Update UI
            self.setWindowTitle(f'SQL Editor - {db_path}')

            # Show status
            self.statusLabel.setText(f"Connected to database: {os.path.basename(db_path)}")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to connect to database: {str(e)}")

    def load_tables(self):
        if not self.conn:
            return

        try:
            self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = self.cursor.fetchall()

            self.tableComboBox.clear()
            table_names = [table[0] for table in tables]
            for table_name in table_names:
                self.tableComboBox.addItem(table_name)

            completer = QCompleter(table_names)
            self.tableComboBox.setCompleter(completer)
            
            self.statusLabel.setText("Tables loaded successfully.")
        except Exception as e:
            self.statusLabel.setText(f"Failed to load tables: {str(e)}")

    def load_table_data(self):
        table_name = self.tableComboBox.currentText()
        if not table_name:
            return

        try:
            self.cursor.execute(f"SELECT * FROM {table_name}")
            data = self.cursor.fetchall()
            self.populate_table(table_name, data)
        except Exception as e:
            self.statusLabel.setText(f"Failed to load table data: {str(e)}")

    def execute_query(self):
        query = self.queryInput.toPlainText().strip()

        try:
            self.cursor.execute(query)
            if query.strip().upper().startswith("SELECT"):
                data = self.cursor.fetchall()
                if data:
                    self.populate_table("Query Result", data)
                self.statusLabel.setText(f"Query executed successfully. {len(data)} rows returned.")
            else:
                self.conn.commit()
                self.statusLabel.setText("Query executed successfully.")
        except Exception as e:
            self.statusLabel.setText(f"Query execution failed: {str(e)}")
            QMessageBox.warning(self, "Query Error", f"Query execution failed: {str(e)}")

    def populate_table(self, table_name, data):
        # Clear existing table contents
        self.resultTable.clear()
        self.resultTable.setRowCount(0)
        self.resultTable.setColumnCount(0)

        # Set table name as objectName for later use
        self.resultTable.setObjectName(table_name)

        # Populate table with data
        self.resultTable.setRowCount(len(data))
        self.resultTable.setColumnCount(len(data[0]))

        # Set headers
        headers = [description[0] for description in self.cursor.description]
        self.resultTable.setHorizontalHeaderLabels(headers)

        # Populate cells
        for i, row_data in enumerate(data):
            for j, value in enumerate(row_data):
                item = QTableWidgetItem(str(value))
                self.resultTable.setItem(i, j, item)

        # Connect cellChanged signal to handle cell edits
        self.resultTable.cellChanged.connect(self.update_database_from_cell)

    def update_database_from_cell(self, row, column):
        if not self.conn:
            return

        try:
            table_name = self.resultTable.objectName()
            if not table_name:
                raise ValueError("Table name is not set.")

            column_name = self.resultTable.horizontalHeaderItem(column).text()
            rowid_item = self.resultTable.item(row, 0)
            if rowid_item:
                rowid = rowid_item.text()
            else:
                raise ValueError("No rowid found for the selected row.")

            new_value = self.resultTable.item(row, column).text()
            update_query = f"UPDATE `{table_name}` SET `{column_name}` = ? WHERE rowid = ?"
            self.cursor.execute(update_query, (new_value, rowid))
            self.conn.commit()

            self.statusLabel.setText("Database updated successfully.")
        except Exception as e:
            self.statusLabel.setText(f"Failed to update database: {str(e)}")

    def toggle_header_info(self, checked):
        if checked:
            table_name = self.tableComboBox.currentText()
            if not table_name:
                header_info = "No table selected."
            else:
                header_info = f"Header Information for Table: {table_name}\n"
                if self.cursor:
                    self.cursor.execute(f"PRAGMA table_info({table_name})")
                    col_info = self.cursor.fetchall()
                    for col in col_info:
                        header_info += f"{col[1]} (type: {col[2]})\n"
            QToolTip.showText(self.headerInfoButton.mapToGlobal(self.headerInfoButton.rect().bottomLeft()), header_info)
        else:
            QToolTip.hideText()

    def generate_database(self):
        try:
            script_dir = os.path.dirname(os.path.realpath(__file__))
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            db_name = f"{timestamp}.db"
            db_path = os.path.join(script_dir, '..', '..', '..', '..', 'export', "sql", db_name)

            if os.path.exists(db_path):
                os.remove(db_path)

            self.conn = sqlite3.connect(db_path)
            self.cursor = self.conn.cursor()

            sql_file = os.path.join(script_dir, '..', 'scripts', 'gen_db.sql')
            with open(sql_file, 'r') as f:
                sql_commands = f.read()
                self.cursor.executescript(sql_commands)

            self.conn.commit()
            self.statusLabel.setText(f"Database '{db_name}' generated successfully.")

        except Exception as e:
            self.statusLabel.setText(f"Failed to generate database: {str(e)}")

    def open_bank_sql(self):
        bank_sql_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'scripts', 'bank.sql')

        self.progress_dialog = QProgressDialog("Loading Bank SQL file...", None, 0, 0)
        self.progress_dialog.setWindowTitle("Loading")
        self.progress_dialog.setWindowModality(Qt.WindowModal)
        self.progress_dialog.show()

        self.bank_worker = BankSQLWorker(bank_sql_path)
        self.bank_worker.finished.connect(self.show_bank_sql_content)
        self.bank_worker.error.connect(self.show_bank_sql_content)
        self.bank_worker.start()

    def show_bank_sql_content(self, content):
        self.progress_dialog.close()

        if content is None:
            QMessageBox.warning(self, "Error", "Failed to load bank.sql file.")
        else:
            popup = TextPopup(content, self)
            popup.exec_()

    def closeEvent(self, event):
        if self.conn:
            self.conn.close()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Adding application icon
    app_icon = QIcon(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'icon', 'zen.png'))
    app.setWindowIcon(app_icon)

    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())