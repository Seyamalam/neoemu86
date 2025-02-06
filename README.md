# Modern EMU8086

A modern, user-friendly Intel 8086 assembly emulator with a clean and intuitive interface. This emulator provides a better user experience compared to the traditional Emu8086 while maintaining compatibility with 8086 assembly instructions.

## Features

- 🎨 Modern, dark-themed UI with syntax highlighting
- 💻 Real-time register and flag status updates
- 🔍 Memory viewer with hexadecimal display
- ⚡ Step-by-step execution with F8
- 🏃 Full program execution with F5
- 🔄 Reset functionality
- 📝 Built-in code editor with syntax highlighting

## Installation

1. Make sure you have Python 3.8 or newer installed on your system.

2. Clone this repository:
```bash
git clone [repository-url]
cd modern-emu8086
```

3. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Run the emulator:
```bash
python modern_emu8086.py
```

2. Write or paste your 8086 assembly code in the editor.

3. Use the following controls:
   - Click "Run" or press F5 to execute the entire program
   - Click "Step" or press F8 to execute one instruction at a time
   - Click "Reset" to clear all registers and memory

## Supported Instructions

Currently supported 8086 instructions include:
- `MOV` - Move data between registers or load immediate values
- `ADD` - Add two values
- `SUB` - Subtract two values

More instructions will be added in future updates.

## Example Code

```assembly
; Sample 8086 Assembly Code
mov ax, 1234    ; Load immediate value into AX
mov bx, 5678    ; Load immediate value into BX
add ax, bx      ; Add BX to AX
mov cx, ax      ; Copy result to CX
```

## Contributing

Contributions are welcome! Feel free to submit issues and pull requests.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 