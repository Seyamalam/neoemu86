class Register:
    def __init__(self, name, size=16):
        self.name = name
        self.size = size
        self.value = 0

    def set(self, value):
        mask = (1 << self.size) - 1
        self.value = value & mask

    def get(self):
        return self.value

class Flags:
    def __init__(self):
        self.zero = False      # Zero flag (ZF)
        self.sign = False      # Sign flag (SF)
        self.carry = False     # Carry flag (CF)
        self.overflow = False  # Overflow flag (OF)
        self.auxiliary = False # Auxiliary flag (AF)
        self.parity = False   # Parity flag (PF)

    def update_flags(self, result, size=16):
        mask = (1 << size) - 1
        result &= mask

        # Zero flag
        self.zero = (result == 0)

        # Sign flag
        self.sign = bool(result & (1 << (size - 1)))

        # Parity flag
        self.parity = bin(result).count('1') % 2 == 0

class DataSegment:
    def __init__(self):
        self.variables = {}
        self.memory = bytearray(65536)
        self.current_offset = 0

    def define_variable(self, name, value, size=1):
        """Define a variable in the data segment"""
        self.variables[name] = {
            'offset': self.current_offset,
            'size': size,
            'value': value
        }
        if isinstance(value, str):
            # Store string in memory
            for i, char in enumerate(value):
                if char == '$':  # End of string marker
                    break
                self.memory[self.current_offset + i] = ord(char)
            self.memory[self.current_offset + len(value)] = ord('$')  # Add string terminator
            self.current_offset += len(value) + 1
        else:
            # Store numeric value
            self.memory[self.current_offset] = value
            self.current_offset += size

    def get_variable_offset(self, name):
        """Get the offset of a variable"""
        if name in self.variables:
            return self.variables[name]['offset']
        raise ValueError(f"Undefined variable: {name}")

    def get_memory_byte(self, offset):
        """Get a byte from memory"""
        return self.memory[offset]

    def set_memory_byte(self, offset, value):
        """Set a byte in memory"""
        self.memory[offset] = value & 0xFF

class Emulator:
    def __init__(self):
        # Initialize registers
        self.registers = {
            'ax': Register('ax'),
            'bx': Register('bx'),
            'cx': Register('cx'),
            'dx': Register('dx'),
            'si': Register('si'),
            'di': Register('di'),
            'bp': Register('bp'),
            'sp': Register('sp'),
            'ds': Register('ds')
        }

        # Initialize 8-bit registers
        self.registers.update({
            'al': Register('al', 8),
            'ah': Register('ah', 8),
            'bl': Register('bl', 8),
            'bh': Register('bh', 8),
            'cl': Register('cl', 8),
            'ch': Register('ch', 8),
            'dl': Register('dl', 8),
            'dh': Register('dh', 8)
        })

        # Initialize flags
        self.flags = Flags()
        
        # Initialize segments
        self.data_segment = DataSegment()
        self.stack_size = 256  # Default stack size
        
        # Program counter
        self.ip = 0
        
        # Current segment being processed
        self.current_segment = None
        
        # Current procedure
        self.current_proc = None

    def reset(self):
        """Reset the emulator state"""
        for reg in self.registers.values():
            reg.set(0)
        self.flags = Flags()
        self.data_segment = DataSegment()
        self.ip = 0
        self.current_segment = None
        self.current_proc = None

    def parse_program(self, code):
        """Parse the assembly program and set up segments"""
        lines = [line.strip() for line in code.split('\n')]
        current_segment = None
        
        for line in lines:
            if not line or line.startswith(';'):
                continue

            # Remove comments
            line = line.split(';')[0].strip()
            tokens = line.lower().split()
            
            if not tokens:
                continue

            if tokens[0] == '.model':
                if len(tokens) > 1:
                    self.model = tokens[1]
            
            elif tokens[0] == '.stack':
                if len(tokens) > 1:
                    self.stack_size = int(tokens[1].rstrip('h'), 16)
                current_segment = 'stack'
            
            elif tokens[0] == '.data':
                current_segment = 'data'
            
            elif tokens[0] == '.code':
                current_segment = 'code'
            
            elif current_segment == 'data':
                if len(tokens) >= 3 and tokens[1] == 'db':
                    # Handle data definition
                    var_name = tokens[0]
                    if var_name.endswith(','):
                        var_name = var_name[:-1]
                    
                    # Handle string literals
                    if line.find("'") != -1:
                        value = line[line.find("'"):line.rfind("'") + 1]
                        value = value.strip("'")
                    else:
                        # Handle numeric or special values
                        value = tokens[2]
                        if value == '?':
                            value = 0
                        elif value.isdigit():
                            value = int(value)
                        else:
                            value = 0
                    
                    self.data_segment.define_variable(var_name, value)

    def get_register_value(self, reg_name):
        """Get the value of a register"""
        reg_name = reg_name.lower().strip()
        if reg_name in self.registers:
            return self.registers[reg_name].get()
        raise ValueError(f"Invalid register name: {reg_name}")

    def set_register_value(self, reg_name, value):
        """Set the value of a register"""
        reg_name = reg_name.lower().strip()
        if reg_name in self.registers:
            self.registers[reg_name].set(value)
            # Update the corresponding 16-bit register for 8-bit registers
            if reg_name in ['al', 'ah']:
                ax_value = (self.registers['ah'].get() << 8) | self.registers['al'].get()
                self.registers['ax'].set(ax_value)
            elif reg_name in ['bl', 'bh']:
                bx_value = (self.registers['bh'].get() << 8) | self.registers['bl'].get()
                self.registers['bx'].set(bx_value)
            elif reg_name in ['cl', 'ch']:
                cx_value = (self.registers['ch'].get() << 8) | self.registers['cl'].get()
                self.registers['cx'].set(cx_value)
            elif reg_name in ['dl', 'dh']:
                dx_value = (self.registers['dh'].get() << 8) | self.registers['dl'].get()
                self.registers['dx'].set(dx_value)
            
            # Also update 8-bit registers when 16-bit register is modified
            if reg_name == 'ax':
                self.registers['ah'].set((value >> 8) & 0xFF)
                self.registers['al'].set(value & 0xFF)
            elif reg_name == 'bx':
                self.registers['bh'].set((value >> 8) & 0xFF)
                self.registers['bl'].set(value & 0xFF)
            elif reg_name == 'cx':
                self.registers['ch'].set((value >> 8) & 0xFF)
                self.registers['cl'].set(value & 0xFF)
            elif reg_name == 'dx':
                self.registers['dh'].set((value >> 8) & 0xFF)
                self.registers['dl'].set(value & 0xFF)
        else:
            raise ValueError(f"Invalid register name: {reg_name}")

    def execute_instruction(self, instruction):
        """Execute a single assembly instruction"""
        tokens = instruction.lower().split()
        if not tokens:
            return

        # Handle procedure declarations
        if len(tokens) > 1 and tokens[1] == 'proc':
            self.current_proc = tokens[0]
            return
        elif tokens[0] == 'endp':
            self.current_proc = None
            return
        elif tokens[0] == 'end':
            return

        opcode = tokens[0].strip()
        if len(tokens) > 1:
            # Split operands and handle whitespace properly
            operands = [op.strip() for op in ' '.join(tokens[1:]).split(',')]
        else:
            operands = []

        if opcode == 'mov':
            if len(operands) != 2:
                raise ValueError("MOV instruction requires two operands")
            dest, source = operands
            
            # Handle destination
            if dest in self.registers:
                # Moving to register
                source = source.strip()
                if source == '@data':  # Special case for data segment
                    value = 0  # Simplified data segment handling
                elif source.startswith('0x'):
                    value = int(source[2:], 16)
                elif source.endswith('h'):  # Handle hexadecimal values
                    value = int(source[:-1], 16)
                elif source.isdigit():
                    value = int(source)
                elif source in self.registers:
                    value = self.get_register_value(source)
                else:
                    # Try to get value from memory variable
                    try:
                        value = self.data_segment.get_memory_byte(self.data_segment.get_variable_offset(source))
                    except ValueError:
                        raise ValueError(f"Invalid source operand: {source}")
                self.set_register_value(dest, value)
            else:
                # Moving to memory
                try:
                    dest_offset = self.data_segment.get_variable_offset(dest)
                    if source.startswith('0x'):
                        value = int(source[2:], 16)
                    elif source.endswith('h'):  # Handle hexadecimal values
                        value = int(source[:-1], 16)
                    elif source.isdigit():
                        value = int(source)
                    else:
                        value = self.get_register_value(source)
                    self.data_segment.set_memory_byte(dest_offset, value)
                except ValueError:
                    raise ValueError(f"Invalid destination operand: {dest}")

        elif opcode == 'add':
            if len(operands) != 2:
                raise ValueError("ADD instruction requires two operands")
            dest, source = operands
            
            # Get destination value
            if dest in self.registers:
                dest_val = self.get_register_value(dest)
            else:
                try:
                    dest_offset = self.data_segment.get_variable_offset(dest)
                    dest_val = self.data_segment.get_memory_byte(dest_offset)
                except ValueError:
                    raise ValueError(f"Invalid destination operand: {dest}")
            
            # Get source value
            source = source.strip()
            if source.startswith('0x'):
                source_val = int(source[2:], 16)
            elif source.endswith('h'):  # Handle hexadecimal values
                source_val = int(source[:-1], 16)
            elif source.isdigit():
                source_val = int(source)
            elif source == "'0'":  # Handle ASCII '0'
                source_val = ord('0')
            elif source in self.registers:
                source_val = self.get_register_value(source)
            else:
                try:
                    source_offset = self.data_segment.get_variable_offset(source)
                    source_val = self.data_segment.get_memory_byte(source_offset)
                except ValueError:
                    raise ValueError(f"Invalid source operand: {source}")
            
            result = dest_val + source_val
            
            # Store result
            if dest in self.registers:
                self.set_register_value(dest, result)
            else:
                self.data_segment.set_memory_byte(dest_offset, result)
            
            self.flags.update_flags(result)

        elif opcode == 'sub':
            if len(operands) != 2:
                raise ValueError("SUB instruction requires two operands")
            dest, source = operands
            
            # Get destination value
            if dest in self.registers:
                dest_val = self.get_register_value(dest)
            else:
                try:
                    dest_offset = self.data_segment.get_variable_offset(dest)
                    dest_val = self.data_segment.get_memory_byte(dest_offset)
                except ValueError:
                    raise ValueError(f"Invalid destination operand: {dest}")
            
            # Get source value
            source = source.strip()
            if source.startswith('0x'):
                source_val = int(source[2:], 16)
            elif source.endswith('h'):  # Handle hexadecimal values
                source_val = int(source[:-1], 16)
            elif source.isdigit():
                source_val = int(source)
            elif source == "'0'":  # Handle ASCII '0'
                source_val = ord('0')
            elif source in self.registers:
                source_val = self.get_register_value(source)
            else:
                try:
                    source_offset = self.data_segment.get_variable_offset(source)
                    source_val = self.data_segment.get_memory_byte(source_offset)
                except ValueError:
                    raise ValueError(f"Invalid source operand: {source}")
            
            result = dest_val - source_val
            
            # Store result
            if dest in self.registers:
                self.set_register_value(dest, result)
            else:
                self.data_segment.set_memory_byte(dest_offset, result)
            
            self.flags.update_flags(result)

        elif opcode == 'lea':
            if len(operands) != 2:
                raise ValueError("LEA instruction requires two operands")
            dest, source = operands
            # Get the offset of the variable and store it in the destination register
            offset = self.data_segment.get_variable_offset(source)
            self.set_register_value(dest, offset)

        elif opcode == 'int':
            if len(operands) != 1:
                raise ValueError("INT instruction requires one operand")
            interrupt = operands[0].strip()
            if interrupt == '21h' or interrupt == '21':
                self.handle_int_21h()
            else:
                raise ValueError(f"Unsupported interrupt: {interrupt}")

    def handle_int_21h(self):
        """Handle INT 21h services"""
        service = self.get_register_value('ah')
        
        if service == 1:  # Single character input
            char = input()
            if char:
                self.set_register_value('al', ord(char[0]))
                print(char[0])
            
        elif service == 2:  # Display character
            char = chr(self.get_register_value('dl'))
            print(char, end='', flush=True)
            
        elif service == 9:  # Display string
            offset = self.get_register_value('dx')
            # Read string from memory until '$'
            output = ""
            while True:
                char = chr(self.data_segment.get_memory_byte(offset))
                if char == '$':
                    break
                output += char
                offset += 1
            print(output, end='', flush=True)
                
        elif service == 0x4c or service == 76:  # Program termination (76 is decimal for 0x4C)
            print("\nProgram terminated.")

    def get_memory_byte(self, address):
        """Get a byte from memory"""
        return self.data_segment.get_memory_byte(address)

    def set_memory_byte(self, address, value):
        """Set a byte in memory"""
        self.data_segment.set_memory_byte(address, value)

    def get_flags_state(self):
        """Get the current state of all flags"""
        return {
            'ZF': int(self.flags.zero),
            'SF': int(self.flags.sign),
            'CF': int(self.flags.carry),
            'OF': int(self.flags.overflow),
            'AF': int(self.flags.auxiliary),
            'PF': int(self.flags.parity)
        } 