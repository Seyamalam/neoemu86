import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                           QHBoxLayout, QTextEdit, QLabel, QPushButton,
                           QTableWidget, QTableWidgetItem, QTabWidget, QMessageBox,
                           QInputDialog, QLineEdit)
from PyQt6.QtGui import QFont, QPalette, QColor, QSyntaxHighlighter, QTextCharFormat, QKeySequence, QShortcut
from PyQt6.QtCore import Qt
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
            "jl", "jle", "jg", "jge", "push", "pop", "int"
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
            "si", "di", "sp", "bp"
        ]
        for reg in registers:
            pattern = f"\\b{reg}\\b"
            self.highlighting_rules.append((pattern, register_format))

        # Numbers
        number_format = QTextCharFormat()
        number_format.setForeground(QColor("#B5CEA8"))
        self.highlighting_rules.append(("\\b[0-9]+\\b", number_format))

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

class ModernEmu8086(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Modern EMU8086")
        self.setMinimumSize(1200, 800)
        
        # Initialize emulator
        self.emulator = Emulator()
        
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
            }
            QPushButton:hover {
                background-color: #1177BB;
            }
            QTableWidget {
                background-color: #252526;
                border: 1px solid #3C3C3C;
                border-radius: 4px;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QLabel {
                color: #D4D4D4;
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
                padding: 5px 10px;
            }
            QTabBar::tab:selected {
                background-color: #1E1E1E;
                border-bottom-color: #1E1E1E;
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
        
        # Code editor
        self.code_editor = QTextEdit()
        self.code_editor.setFont(QFont("Consolas", 12))
        self.highlighter = AssemblyHighlighter(self.code_editor.document())
        
        # Add sample code for adding numbers with input
        sample_code = "; Program to add two numbers with input\n\n"
        sample_code += "; Display first prompt\n"
        sample_code += "lea dx, msg1\n"
        sample_code += "mov ah, 9\n"
        sample_code += "int 21h\n\n"
        sample_code += "; Get first number\n"
        sample_code += "mov ah, 1\n"
        sample_code += "int 21h\n"
        sample_code += "sub al, '0'\n"
        sample_code += "mov bl, al\n\n"
        sample_code += "; New line\n"
        sample_code += "lea dx, newline\n"
        sample_code += "mov ah, 9\n"
        sample_code += "int 21h\n\n"
        sample_code += "; Display second prompt\n"
        sample_code += "lea dx, msg2\n"
        sample_code += "mov ah, 9\n"
        sample_code += "int 21h\n\n"
        sample_code += "; Get second number\n"
        sample_code += "mov ah, 1\n"
        sample_code += "int 21h\n"
        sample_code += "sub al, '0'\n\n"
        sample_code += "; Add numbers\n"
        sample_code += "add al, bl\n"
        sample_code += "add al, '0'\n"
        sample_code += "mov dl, al\n\n"
        sample_code += "; New line\n"
        sample_code += "lea dx, newline\n"
        sample_code += "mov ah, 9\n"
        sample_code += "int 21h\n\n"
        sample_code += "; Display result message\n"
        sample_code += "lea dx, result_msg\n"
        sample_code += "mov ah, 9\n"
        sample_code += "int 21h\n\n"
        sample_code += "; Display result\n"
        sample_code += "mov ah, 2\n"
        sample_code += "int 21h\n\n"
        sample_code += "; Exit program\n"
        sample_code += "mov ah, 4ch\n"
        sample_code += "int 21h"
        
        self.code_editor.setText(sample_code)
        
        left_layout.addWidget(QLabel("Code Editor"))
        left_layout.addWidget(self.code_editor)

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
        flags_layout.addWidget(self.flags_table)
        tabs.addTab(flags_widget, "Flags")

        right_layout.addWidget(tabs)

        # Add panels to top section
        top_layout.addWidget(left_panel, 2)
        top_layout.addWidget(right_panel, 1)

        # Add top section to main layout
        main_layout.addWidget(top_section)

        # Add output console
        output_widget = QWidget()
        output_layout = QVBoxLayout(output_widget)
        output_layout.addWidget(QLabel("Output Console"))
        self.output_console = QTextEdit()
        self.output_console.setReadOnly(True)
        self.output_console.setFont(QFont("Consolas", 12))
        self.output_console.setStyleSheet("""
            QTextEdit {
                background-color: #1E1E1E;
                color: #D4D4D4;
                border: 1px solid #3C3C3C;
            }
        """)
        output_layout.addWidget(self.output_console)
        main_layout.addWidget(output_widget, 1)

        # Initialize tables
        self.initialize_tables()
        
        # Current instruction pointer for stepping
        self.current_line = 0
        self.program_lines = []

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
            self.registers_table.setItem(i, 1, QTableWidgetItem(f"{val:04X}"))

        # Update flags
        flags_state = self.emulator.get_flags_state()
        flag_names = ["ZF", "SF", "CF", "OF", "AF", "PF"]
        for i, flag in enumerate(flag_names):
            self.flags_table.setItem(i, 1, QTableWidgetItem(str(flags_state[flag])))

        # Update memory display
        for i in range(16):
            for j in range(16):
                addr = i * 16 + j
                value = self.emulator.get_memory_byte(addr)
                self.memory_table.setItem(i, j+1, QTableWidgetItem(f"{value:02X}"))

        # Update output console
        output = self.emulator.get_output()
        if output:
            self.output_console.append(output)
            if "Waiting for input:" in output:
                text, ok = QInputDialog.getText(self, 'Input Required', 
                                             'Enter a single digit (0-9):',
                                             QLineEdit.EchoMode.Normal)
                if ok and text and text[0].isdigit():
                    self.emulator.add_input(text[0])
                    self.execute_current_instruction()

    def execute_current_instruction(self):
        if self.current_line < len(self.program_lines):
            instruction = self.program_lines[self.current_line]
            self.emulator.execute_instruction(instruction)
            self.current_line += 1
            self.update_display()

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
            self.output_console.clear()
            
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
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error executing program: {str(e)}")

    def step_program(self):
        try:
            # If this is the first step, prepare the program
            if self.current_line == 0:
                self.emulator.reset()
                self.output_console.clear()
                
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
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error executing instruction: {str(e)}")
            self.current_line = 0

    def reset_emulator(self):
        self.emulator.reset()
        self.current_line = 0
        self.output_console.clear()
        self.update_display()
        QMessageBox.information(self, "Reset", "Emulator has been reset!")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ModernEmu8086()
    window.show()
    sys.exit(app.exec()) 