import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                           QHBoxLayout, QTextEdit, QLabel, QPushButton,
                           QTableWidget, QTableWidgetItem, QTabWidget, QMessageBox,
                           QFileDialog, QStatusBar, QSpinBox, QLineEdit)
from PyQt6.QtGui import (QFont, QPalette, QColor, QSyntaxHighlighter, 
                        QTextCharFormat, QKeySequence, QShortcut, QIcon,
                        QTextCursor)
from PyQt6.QtCore import Qt, QTimer
from emu8086_core import Emulator

class AssemblyHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.highlighting_rules = []

        # Keywords
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor("#569CD6"))
        keyword_format.setFontWeight(QFont.Weight.Bold)
        keywords = [
            "mov", "add", "sub", "mul", "div", "inc", "dec",
            "and", "or", "xor", "not", "jmp", "je", "jne",
            "jl", "jle", "jg", "jge", "push", "pop", "int",
            "proc", "endp", "end"
        ]
        for word in keywords:
            pattern = f"\\b{word}\\b"
            self.highlighting_rules.append((pattern, keyword_format))

        # Registers
        register_format = QTextCharFormat()
        register_format.setForeground(QColor("#4EC9B0"))
        registers = [
            "ax", "bx", "cx", "dx",
            "ah", "al", "bh", "bl",
            "ch", "cl", "dh", "dl",
            "si", "di", "sp", "bp",
            "ds", "es", "ss", "cs"
        ]
        for reg in registers:
            pattern = f"\\b{reg}\\b"
            self.highlighting_rules.append((pattern, register_format))

        # Directives
        directive_format = QTextCharFormat()
        directive_format.setForeground(QColor("#C586C0"))
        directives = [
            ".model", ".stack", ".data", ".code",
            "db", "dw", "dd"
        ]
        for directive in directives:
            pattern = f"\\b{directive}\\b"
            self.highlighting_rules.append((pattern, directive_format))

        # Numbers
        number_format = QTextCharFormat()
        number_format.setForeground(QColor("#B5CEA8"))
        self.highlighting_rules.append(("\\b[0-9]+\\b", number_format))
        self.highlighting_rules.append(("\\b[0-9]+h\\b", number_format))

        # Strings
        string_format = QTextCharFormat()
        string_format.setForeground(QColor("#CE9178"))
        self.highlighting_rules.append(("'[^']*'", string_format))

        # Comments
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor("#6A9955"))
        self.highlighting_rules.append((";.*", comment_format))

    def highlightBlock(self, text):
        for pattern, format in self.highlighting_rules:
            expression = pattern
            index = text.find(expression)
            while index >= 0:
                length = len(expression)
                self.setFormat(index, length, format)
                index = text.find(expression, index + length)

class ConsoleWidget(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(False)
        self.input_ready = False
        self.input_pos = 0
        self.setFont(QFont("Consolas", 12))
        self.setStyleSheet("""
            QTextEdit {
                background-color: #1E1E1E;
                color: #D4D4D4;
                border: 1px solid #3C3C3C;
            }
        """)
        self.waiting_for_input = False
        self.input_text = ""

    def keyPressEvent(self, event):
        if self.waiting_for_input:
            if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
                cursor = self.textCursor()
                cursor.movePosition(QTextCursor.MoveOperation.End)
                cursor.movePosition(QTextCursor.MoveOperation.StartOfBlock, QTextCursor.MoveMode.KeepAnchor)
                text = cursor.selectedText()
                self.input_text = text[text.find("Input: ") + 7:]
                self.insertPlainText("\n")
                self.input_ready = True
                self.waiting_for_input = False
            elif event.key() == Qt.Key.Key_Backspace:
                cursor = self.textCursor()
                if cursor.position() > self.input_pos:
                    super().keyPressEvent(event)
            else:
                cursor = self.textCursor()
                cursor.movePosition(QTextCursor.MoveOperation.End)
                self.setTextCursor(cursor)
                super().keyPressEvent(event)
        else:
            event.ignore()

    def write(self, text):
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.setTextCursor(cursor)
        self.insertPlainText(text)
        self.ensureCursorVisible()

    def get_input(self):
        self.waiting_for_input = True
        self.input_ready = False
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.input_pos = cursor.position()
        
        while not self.input_ready:
            QApplication.processEvents()
        
        return self.input_text

class ModernEmu8086(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Modern EMU8086")
        self.setMinimumSize(1200, 800)
        
        # Initialize emulator
        self.emulator = Emulator()
        self.emulator.set_io_handler(self)
        
        # Set the color scheme
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1E1E1E;
            }
            QWidget {
                background-color: #1E1E1E;
                color: #D4D4D4;
            }
            QTextEdit {
                background-color: #252526;
                border: 1px solid #3C3C3C;
                border-radius: 4px;
                font-family: 'Consolas', monospace;
                padding: 5px;
            }
            QPushButton {
                background-color: #0E639C;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                color: white;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #1177BB;
            }
            QPushButton:disabled {
                background-color: #666666;
            }
            QTableWidget {
                background-color: #252526;
                border: 1px solid #3C3C3C;
                border-radius: 4px;
                gridline-color: #3C3C3C;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QHeaderView::section {
                background-color: #2D2D2D;
                color: #D4D4D4;
                padding: 5px;
                border: 1px solid #3C3C3C;
            }
            QLabel {
                color: #D4D4D4;
                font-weight: bold;
            }
            QTabWidget::pane {
                border: 1px solid #3C3C3C;
                background-color: #252526;
            }
            QTabWidget::tab-bar {
                left: 5px;
            }
            QTabBar::tab {
                background-color: #2D2D2D;
                color: #D4D4D4;
                border: 1px solid #3C3C3C;
                border-bottom-color: #3C3C3C;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                padding: 8px 12px;
                min-width: 80px;
            }
            QTabBar::tab:selected {
                background-color: #1E1E1E;
                border-bottom-color: #1E1E1E;
            }
            QStatusBar {
                background-color: #007ACC;
                color: white;
            }
            QLineEdit {
                background-color: #252526;
                border: 1px solid #3C3C3C;
                border-radius: 4px;
                padding: 5px;
                color: #D4D4D4;
            }
            QSpinBox {
                background-color: #252526;
                border: 1px solid #3C3C3C;
                border-radius: 4px;
                padding: 5px;
                color: #D4D4D4;
            }
        """)

        # Create the central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Top section with code editor and registers
        top_section = QWidget()
        top_layout = QHBoxLayout(top_section)

        # Left panel (Code Editor)
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # Toolbar
        toolbar_layout = QHBoxLayout()
        self.new_button = QPushButton("New")
        self.open_button = QPushButton("Open")
        self.save_button = QPushButton("Save")
        toolbar_layout.addWidget(self.new_button)
        toolbar_layout.addWidget(self.open_button)
        toolbar_layout.addWidget(self.save_button)
        toolbar_layout.addStretch()
        left_layout.addLayout(toolbar_layout)
        
        # Connect toolbar buttons
        self.new_button.clicked.connect(self.new_file)
        self.open_button.clicked.connect(self.open_file)
        self.save_button.clicked.connect(self.save_file)
        
        # Code editor
        self.code_editor = QTextEdit()
        self.code_editor.setFont(QFont("Consolas", 12))
        self.highlighter = AssemblyHighlighter(self.code_editor.document())
        
        # Add line numbers
        self.line_numbers = QTextEdit()
        self.line_numbers.setFont(QFont("Consolas", 12))
        self.line_numbers.setFixedWidth(50)
        self.line_numbers.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.line_numbers.setReadOnly(True)
        
        # Editor layout
        editor_layout = QHBoxLayout()
        editor_layout.addWidget(self.line_numbers)
        editor_layout.addWidget(self.code_editor)
        
        left_layout.addWidget(QLabel("Code Editor"))
        left_layout.addLayout(editor_layout)

        # Buttons
        button_layout = QHBoxLayout()
        self.run_button = QPushButton("Run (F5)")
        self.step_button = QPushButton("Step (F8)")
        self.reset_button = QPushButton("Reset")
        
        # Connect buttons to functions
        self.run_button.clicked.connect(self.run_program)
        self.step_button.clicked.connect(self.step_program)
        self.reset_button.clicked.connect(self.reset_emulator)
        
        # Add keyboard shortcuts
        QShortcut(QKeySequence("F5"), self).activated.connect(self.run_program)
        QShortcut(QKeySequence("F8"), self).activated.connect(self.step_program)
        
        button_layout.addWidget(self.run_button)
        button_layout.addWidget(self.step_button)
        button_layout.addWidget(self.reset_button)
        left_layout.addLayout(button_layout)

        # Right panel (Register view and memory)
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)

        # Tabs for different views
        tabs = QTabWidget()
        
        # Registers tab
        registers_widget = QWidget()
        registers_layout = QVBoxLayout(registers_widget)
        self.registers_table = QTableWidget(8, 2)
        self.registers_table.setHorizontalHeaderLabels(["Register", "Value"])
        self.registers_table.horizontalHeader().setStretchLastSection(True)
        registers_layout.addWidget(self.registers_table)
        tabs.addTab(registers_widget, "Registers")

        # Memory tab
        memory_widget = QWidget()
        memory_layout = QVBoxLayout(memory_widget)
        self.memory_table = QTableWidget(16, 17)
        self.memory_table.setHorizontalHeaderLabels(["Offset"] + [f"+{i:X}" for i in range(16)])
        memory_layout.addWidget(self.memory_table)
        tabs.addTab(memory_widget, "Memory")

        # Flags tab
        flags_widget = QWidget()
        flags_layout = QVBoxLayout(flags_widget)
        self.flags_table = QTableWidget(6, 2)
        self.flags_table.setHorizontalHeaderLabels(["Flag", "Value"])
        self.flags_table.horizontalHeader().setStretchLastSection(True)
        flags_layout.addWidget(self.flags_table)
        tabs.addTab(flags_widget, "Flags")

        right_layout.addWidget(tabs)

        # Add panels to top section
        top_layout.addWidget(left_panel, 2)
        top_layout.addWidget(right_panel, 1)

        # Add top section to main layout
        main_layout.addWidget(top_section)

        # Add console output
        console_widget = QWidget()
        console_layout = QVBoxLayout(console_widget)
        console_layout.addWidget(QLabel("Console"))
        self.console = ConsoleWidget()
        console_layout.addWidget(self.console)
        main_layout.addWidget(console_widget, 1)

        # Add status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

        # Initialize tables
        self.initialize_tables()
        
        # Current instruction pointer for stepping
        self.current_line = 0
        self.program_lines = []
        
        # Update line numbers
        self.code_editor.textChanged.connect(self.update_line_numbers)
        self.update_line_numbers()

    def update_line_numbers(self):
        """Update the line numbers display"""
        text = self.code_editor.toPlainText()
        lines = text.count('\n') + 1
        line_numbers = '\n'.join(str(i) for i in range(1, lines + 1))
        self.line_numbers.setText(line_numbers)
        self.line_numbers.verticalScrollBar().setValue(
            self.code_editor.verticalScrollBar().value()
        )

    def new_file(self):
        """Create a new file"""
        self.code_editor.clear()
        self.reset_emulator()
        self.status_bar.showMessage("New file created")

    def open_file(self):
        """Open an assembly file"""
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Open Assembly File", "", "Assembly Files (*.asm);;All Files (*.*)"
        )
        if file_name:
            try:
                with open(file_name, 'r') as f:
                    self.code_editor.setText(f.read())
                self.status_bar.showMessage(f"Opened {file_name}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error opening file: {str(e)}")

    def save_file(self):
        """Save the current file"""
        file_name, _ = QFileDialog.getSaveFileName(
            self, "Save Assembly File", "", "Assembly Files (*.asm);;All Files (*.*)"
        )
        if file_name:
            try:
                with open(file_name, 'w') as f:
                    f.write(self.code_editor.toPlainText())
                self.status_bar.showMessage(f"Saved to {file_name}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error saving file: {str(e)}")

    def update_display(self):
        # Update registers
        registers = [
            ("AX", self.emulator.get_register_value("ax")),
            ("BX", self.emulator.get_register_value("bx")),
            ("CX", self.emulator.get_register_value("cx")),
            ("DX", self.emulator.get_register_value("dx")),
            ("SI", self.emulator.get_register_value("si")),
            ("DI", self.emulator.get_register_value("di")),
            ("BP", self.emulator.get_register_value("bp")),
            ("SP", self.emulator.get_register_value("sp"))
        ]
        for i, (reg, val) in enumerate(registers):
            self.registers_table.setItem(i, 0, QTableWidgetItem(reg))
            self.registers_table.setItem(i, 1, QTableWidgetItem(f"{val:04X}"))

        # Update flags
        flags_state = self.emulator.get_flags_state()
        flag_names = ["ZF", "SF", "CF", "OF", "AF", "PF"]
        for i, flag in enumerate(flag_names):
            self.flags_table.setItem(i, 0, QTableWidgetItem(flag))
            self.flags_table.setItem(i, 1, QTableWidgetItem(str(flags_state[flag])))

        # Update memory display
        for i in range(16):
            self.memory_table.setItem(i, 0, QTableWidgetItem(f"{i*16:04X}"))
            for j in range(16):
                addr = i * 16 + j
                value = self.emulator.get_memory_byte(addr)
                self.memory_table.setItem(i, j+1, QTableWidgetItem(f"{value:02X}"))

    def initialize_tables(self):
        # Initialize registers
        registers = [
            ("AX", "0000"), ("BX", "0000"),
            ("CX", "0000"), ("DX", "0000"),
            ("SI", "0000"), ("DI", "0000"),
            ("BP", "0000"), ("SP", "0000")
        ]
        for i, (reg, val) in enumerate(registers):
            self.registers_table.setItem(i, 0, QTableWidgetItem(reg))
            self.registers_table.setItem(i, 1, QTableWidgetItem(val))

        # Initialize flags
        flags = [
            ("Zero Flag (ZF)", "0"),
            ("Sign Flag (SF)", "0"),
            ("Carry Flag (CF)", "0"),
            ("Overflow Flag (OF)", "0"),
            ("Auxiliary Flag (AF)", "0"),
            ("Parity Flag (PF)", "0")
        ]
        for i, (flag, val) in enumerate(flags):
            self.flags_table.setItem(i, 0, QTableWidgetItem(flag))
            self.flags_table.setItem(i, 1, QTableWidgetItem(val))

        # Initialize memory view
        for i in range(16):
            self.memory_table.setItem(i, 0, QTableWidgetItem(f"{i*16:04X}"))
            for j in range(16):
                self.memory_table.setItem(i, j+1, QTableWidgetItem("00"))

    def run_program(self):
        try:
            # Reset the emulator
            self.emulator.reset()
            self.console.clear()
            
            # Get code from editor
            code = self.code_editor.toPlainText()
            
            # Parse the program first
            self.emulator.parse_program(code)
            
            # Split into lines and filter out empty lines and comments
            self.program_lines = []
            lines = code.split('\n')
            in_code_segment = False
            
            for line in lines:
                line = line.strip()
                if not line or line.startswith(';'):
                    continue
                    
                # Remove comments
                line = line.split(';')[0].strip()
                
                # Check for segments
                if line.lower().startswith('.model') or \
                   line.lower().startswith('.stack') or \
                   line.lower().startswith('.data'):
                    continue
                    
                if line.lower().startswith('.code'):
                    in_code_segment = True
                    continue
                
                if in_code_segment and line:
                    self.program_lines.append(line)
            
            # Execute all instructions
            self.current_line = 0
            while self.current_line < len(self.program_lines):
                self.execute_current_instruction()
            
            self.status_bar.showMessage("Program executed successfully")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error executing program: {str(e)}")
            self.status_bar.showMessage("Error executing program")

    def execute_current_instruction(self):
        if self.current_line < len(self.program_lines):
            instruction = self.program_lines[self.current_line]
            try:
                self.emulator.execute_instruction(instruction)
                self.current_line += 1
                self.update_display()
                
                # Handle input/output
                if "Enter" in instruction or "Result" in instruction:
                    self.console.write(instruction)
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error executing instruction: {str(e)}")
                self.current_line = 0

    def step_program(self):
        try:
            # If this is the first step, prepare the program
            if self.current_line == 0:
                self.emulator.reset()
                self.console.clear()
                
                # Get code from editor
                code = self.code_editor.toPlainText()
                
                # Parse the program first
                self.emulator.parse_program(code)
                
                # Split into lines and filter out empty lines and comments
                self.program_lines = []
                lines = code.split('\n')
                in_code_segment = False
                
                for line in lines:
                    line = line.strip()
                    if not line or line.startswith(';'):
                        continue
                        
                    # Remove comments
                    line = line.split(';')[0].strip()
                    
                    # Check for segments
                    if line.lower().startswith('.model') or \
                       line.lower().startswith('.stack') or \
                       line.lower().startswith('.data'):
                        continue
                        
                    if line.lower().startswith('.code'):
                        in_code_segment = True
                        continue
                    
                    if in_code_segment and line:
                        self.program_lines.append(line)
            
            # Execute the next instruction
            self.execute_current_instruction()
            
            # Check if program is complete
            if self.current_line >= len(self.program_lines):
                QMessageBox.information(self, "End of Program", "Program execution completed!")
                self.current_line = 0
                self.status_bar.showMessage("Program execution completed")
            else:
                self.status_bar.showMessage(f"Executed instruction {self.current_line}")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error executing instruction: {str(e)}")
            self.current_line = 0
            self.status_bar.showMessage("Error in program execution")

    def reset_emulator(self):
        self.emulator.reset()
        self.current_line = 0
        self.console.clear()
        self.update_display()
        self.status_bar.showMessage("Emulator reset")

    def handle_input(self):
        """Handle input request from the emulator"""
        self.console.write("Input: ")
        input_text = self.console.get_input()
        return input_text

    def handle_output(self, text):
        """Handle output from the emulator"""
        self.console.write(text)

def main():
    app = QApplication(sys.argv)
    window = ModernEmu8086()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main() 