from emu8086_core import Emulator
import sys

def main():
    if len(sys.argv) != 2:
        print("Usage: python run_emu8086.py <assembly_file>")
        sys.exit(1)

    # Read the assembly file
    try:
        with open(sys.argv[1], 'r') as f:
            code = f.read()
    except FileNotFoundError:
        print(f"Error: File {sys.argv[1]} not found")
        sys.exit(1)

    # Initialize emulator
    emu = Emulator()
    
    try:
        # Parse the program
        emu.parse_program(code)
        
        # Extract code segment instructions
        lines = code.split('\n')
        instructions = []
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
                instructions.append(line)
        
        # Execute instructions
        for instruction in instructions:
            emu.execute_instruction(instruction)
            
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main() 