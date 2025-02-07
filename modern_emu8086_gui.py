import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                           QHBoxLayout, QTextEdit, QLabel, QPushButton,
                           QTableWidget, QTableWidgetItem, QTabWidget, QMessageBox,
                           QFileDialog, QStatusBar, QSpinBox, QLineEdit, QFrame,
                           QGridLayout, QHeaderView, QInputDialog)
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
        self.setWindowTitle("NeoEmu86 - 8086 Assembler")
        self.setMinimumSize(1400, 900)
        
        # Set dark theme
        self.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #1E1E1E;
                color: #D4D4D4;
            }
            QTextEdit, QTableWidget {
                background-color: #252526;
                border: 1px solid #3C3C3C;
                border-radius: 2px;
                font-family: 'Consolas', monospace;
                padding: 5px;
            }
            QPushButton {
                background-color: #2D2D2D;
                border: 1px solid #3C3C3C;
                border-radius: 2px;
                padding: 5px 10px;
                color: #D4D4D4;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #3E3E3E;
            }
            QPushButton:pressed {
                background-color: #0E639C;
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
                padding: 2px;
            }
            QFrame {
                border: 1px solid #3C3C3C;
                border-radius: 2px;
            }
            QStatusBar {
                background-color: #007ACC;
                color: white;
            }
        """)

        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)

        # Left panel (Code and Controls)
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)

        # Toolbar
        toolbar = QWidget()
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(0, 0, 0, 0)

        # Control buttons
        self.load_btn = QPushButton("Load")
        self.run_btn = QPushButton("Run")
        self.step_btn = QPushButton("Step")
        self.microstep_btn = QPushButton("Microstep")
        self.pause_btn = QPushButton("Pause")
        self.stop_btn = QPushButton("Stop")

        toolbar_layout.addWidget(self.load_btn)
        toolbar_layout.addWidget(self.run_btn)
        toolbar_layout.addWidget(self.step_btn)
        toolbar_layout.addWidget(self.microstep_btn)
        toolbar_layout.addWidget(self.pause_btn)
        toolbar_layout.addWidget(self.stop_btn)
        toolbar_layout.addStretch()

        left_layout.addWidget(toolbar)

        # Code editor with line numbers and addresses
        code_widget = QWidget()
        code_layout = QHBoxLayout(code_widget)
        
        # Address column
        self.address_widget = QTextEdit()
        self.address_widget.setFixedWidth(100)
        self.address_widget.setReadOnly(True)
        
        # Line numbers
        self.line_numbers = QTextEdit()
        self.line_numbers.setFixedWidth(50)
        self.line_numbers.setReadOnly(True)
        
        # Code editor
        self.code_editor = QTextEdit()
        self.highlighter = AssemblyHighlighter(self.code_editor.document())
        
        code_layout.addWidget(self.address_widget)
        code_layout.addWidget(self.line_numbers)
        code_layout.addWidget(self.code_editor)
        
        left_layout.addWidget(code_widget)

        # Right panel (Debug info)
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)

        # Top section: General Purpose and Flag registers
        top_debug = QWidget()
        top_debug_layout = QHBoxLayout(top_debug)

        # General Purpose Registers
        gp_registers = QFrame()
        gp_layout = QGridLayout(gp_registers)
        gp_layout.addWidget(QLabel("General Purpose"), 0, 0, 1, 2)
        
        reg_names = ['AX', 'BX', 'CX', 'DX', 'SI', 'DI', 'BP', 'SP']
        self.reg_values = {}
        
        for i, reg in enumerate(reg_names):
            gp_layout.addWidget(QLabel(reg), i+1, 0)
            value_label = QLabel("0000")
            value_label.setStyleSheet("font-family: 'Consolas'; color: #569CD6;")
            self.reg_values[reg] = value_label
            gp_layout.addWidget(value_label, i+1, 1)

        # Flag Register
        flag_register = QFrame()
        flag_layout = QGridLayout(flag_register)
        flag_layout.addWidget(QLabel("Flag Register"), 0, 0, 1, 2)
        
        flag_names = ['CF', 'PF', 'AF', 'ZF', 'SF', 'TF', 'IF', 'DF', 'OF']
        self.flag_values = {}
        
        for i, flag in enumerate(flag_names):
            flag_layout.addWidget(QLabel(flag), i+1, 0)
            value_label = QLabel("0")
            value_label.setStyleSheet("font-family: 'Consolas'; color: #4EC9B0;")
            self.flag_values[flag] = value_label
            flag_layout.addWidget(value_label, i+1, 1)

        top_debug_layout.addWidget(gp_registers)
        top_debug_layout.addWidget(flag_register)

        # Middle section: Code Segment and Stack
        middle_debug = QWidget()
        middle_debug_layout = QHBoxLayout(middle_debug)

        # Code Segment
        code_segment = QFrame()
        code_segment_layout = QVBoxLayout(code_segment)
        code_segment_layout.addWidget(QLabel("Code Segment"))
        self.code_segment_table = QTableWidget(16, 2)
        self.code_segment_table.setHorizontalHeaderLabels(["Offset", "Instruction"])
        code_segment_layout.addWidget(self.code_segment_table)

        # Stack
        stack = QFrame()
        stack_layout = QVBoxLayout(stack)
        stack_layout.addWidget(QLabel("Stack"))
        self.stack_table = QTableWidget(16, 2)
        self.stack_table.setHorizontalHeaderLabels(["Address", "Value"])
        stack_layout.addWidget(self.stack_table)

        middle_debug_layout.addWidget(code_segment)
        middle_debug_layout.addWidget(stack)

        # Bottom section: Console output
        console = QFrame()
        console_layout = QVBoxLayout(console)
        console_layout.addWidget(QLabel("Console"))
        self.console = QTextEdit()
        self.console.setReadOnly(True)
        console_layout.addWidget(self.console)

        # Add all sections to right panel
        right_layout.addWidget(top_debug)
        right_layout.addWidget(middle_debug)
        right_layout.addWidget(console)

        # Add panels to main layout
        main_layout.addWidget(left_panel, 2)
        main_layout.addWidget(right_panel, 1)

        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

        # Connect signals
        self.load_btn.clicked.connect(self.load_file)
        self.run_btn.clicked.connect(self.run_program)
        self.step_btn.clicked.connect(self.step_program)
        self.stop_btn.clicked.connect(self.reset_emulator)
        
        # Initialize emulator
        self.emulator = Emulator()
        self.emulator.set_io_handler(self)
        self.current_line = 0
        self.program_lines = []

        # Update line numbers when text changes
        self.code_editor.textChanged.connect(self.update_line_numbers)
        self.update_line_numbers()

    def update_line_numbers(self):
        """Update line numbers and addresses"""
        text = self.code_editor.toPlainText()
        lines = text.count('\n') + 1
        
        # Update line numbers
        line_numbers = '\n'.join(str(i) for i in range(1, lines + 1))
        self.line_numbers.setText(line_numbers)
        
        # Update addresses (assuming each instruction is 3 bytes)
        addresses = '\n'.join(f"{i*3:04X}" for i in range(lines))
        self.address_widget.setText(addresses)

    def update_registers(self):
        """Update register display"""
        for reg, label in self.reg_values.items():
            value = self.emulator.get_register_value(reg.lower())
            label.setText(f"{value:04X}")

    def update_flags(self):
        """Update flags display"""
        flags_state = self.emulator.get_flags_state()
        for flag, label in self.flag_values.items():
            if flag in flags_state:
                label.setText(str(flags_state[flag]))

    def update_code_segment(self):
        """Update code segment display"""
        for i, instruction in enumerate(self.program_lines[:16]):
            self.code_segment_table.setItem(i, 0, QTableWidgetItem(f"{i*3:04X}"))
            self.code_segment_table.setItem(i, 1, QTableWidgetItem(instruction))
            if i == self.current_line:
                for j in range(2):
                    item = self.code_segment_table.item(i, j)
                    if item:
                        item.setBackground(QColor("#264F78"))

    def handle_output(self, text):
        """Handle output from the emulator"""
        self.console.append(text)

    def handle_input(self):
        """Handle input request from the emulator"""
        text, ok = QInputDialog.getText(self, 'Input Required', 'Enter value:')
        if ok and text:
            return text
        return None

    def load_file(self):
        """Load an assembly file"""
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

    def run_program(self):
        try:
            # Reset the emulator
            self.emulator.reset()
            self.console.clear()
            
            # Get code from editor
            code = self.code_editor.toPlainText()
            
            # Parse the program first
            self.emulator.parse_program(code)
            
            # Get the instructions from the emulator
            self.program_lines = self.emulator.instructions
            
            # Execute all instructions
            self.current_line = 0
            while self.current_line < len(self.program_lines):
                self.execute_current_instruction()
                QApplication.processEvents()  # Allow GUI updates
            
            self.status_bar.showMessage("Program executed successfully")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error executing program: {str(e)}")
            self.status_bar.showMessage("Error executing program")

    def execute_current_instruction(self):
        if self.current_line < len(self.program_lines):
            instruction = self.program_lines[self.current_line]
            try:
                result = self.emulator.execute_instruction(instruction)
                if result == "jump":
                    # Update current_line based on emulator's instruction index
                    self.current_line = self.emulator.current_instruction_index
                else:
                    self.current_line += 1
                self.update_display()
                
                # Handle input/output
                if "Enter" in instruction or "Result" in instruction:
                    self.console.write(instruction + "\n")
                
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
                
                # Get the instructions from the emulator
                self.program_lines = self.emulator.instructions
            
            # Execute the next instruction
            self.execute_current_instruction()
            
            # Check if program is complete
            if self.current_line >= len(self.program_lines):
                QMessageBox.information(self, "End of Program", "Program execution completed!")
                self.current_line = 0
                self.status_bar.showMessage("Program execution completed")
            else:
                self.status_bar.showMessage(f"Executed instruction {self.current_line + 1} of {len(self.program_lines)}")
                
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

    def update_display(self):
        # Update registers
        self.update_registers()

        # Update flags
        self.update_flags()

        # Update code segment
        self.update_code_segment()

        # Update stack
        for i in range(16):
            self.stack_table.setItem(i, 0, QTableWidgetItem(f"{i*16:04X}"))
            for j in range(16):
                addr = i * 16 + j
                value = self.emulator.get_memory_byte(addr)
                self.stack_table.setItem(i, j+1, QTableWidgetItem(f"{value:02X}"))

    def load_file(self):
        """Load an assembly file"""
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

def main():
    app = QApplication(sys.argv)
    window = ModernEmu8086()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main() 