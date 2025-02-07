.model small
.stack 100h
.data
    msg1 db 'Enter first number: $'   ; Message to prompt for the first number
    msg2 db 'Enter second number: $'  ; Message to prompt for the second number
    msg3 db 'Choose operation (+, -, *, /): $' ; Message to prompt for operation
    result_msg db 'Result: $'         ; Message to display the result
    error_msg db 'Error: Division by zero$' ; Message for division by zero
    newline db 13, 10, '$'            ; Carriage return and line feed for new line
    num1 db ?                         ; Variable to store the first number
    num2 db ?                         ; Variable to store the second number
    operation db ?                    ; Variable to store the operation
    result db ?                       ; Variable to store the result

.code
main proc
    mov ax, @data                     ; Initialize data segment
    mov ds, ax

    lea dx, msg1                      ; Load address of the first prompt message
    mov ah, 9                         ; DOS interrupt for displaying string
    int 21h
    mov ah, 1                         ; DOS interrupt for single character input
    int 21h
    sub al, '0'                       ; Convert ASCII to numeric value
    mov num1, al                      ; Store the input in num1
    lea dx, newline                   ; Load address of the newline
    mov ah, 9                         ; Print newline
    int 21h

    lea dx, msg2                      ; Load address of the second prompt message
    mov ah, 9                         ; Display the second prompt
    int 21h
    mov ah, 1                         ; Wait for single character input
    int 21h
    sub al, '0'                       ; Convert ASCII to numeric value
    mov num2, al                      ; Store the input in num2
    lea dx, newline                   ; Load address of the newline
    mov ah, 9                         ; Print newline
    int 21h

    lea dx, msg3                      ; Load address of the operation prompt
    mov ah, 9                         ; Display the operation prompt
    int 21h
    mov ah, 1                         ; Wait for single character input
    int 21h
    mov operation, al                 ; Store the operation
    lea dx, newline                   ; Load address of the newline
    mov ah, 9                         ; Print newline
    int 21h

    ; Perform the selected operation
    cmp operation, '+'
    je addition
    cmp operation, '-'
    je subtraction
    cmp operation, '*'
    je multiplication
    cmp operation, '/'
    je division
    jmp exit_program

addition:
    mov al, num1                      ; Load the first number into AL
    add al, num2                      ; Add the second number
    add al, '0'                       ; Convert result to ASCII
    mov result, al
    jmp display_result

subtraction:
    mov al, num1                      ; Load the first number into AL
    sub al, num2                      ; Subtract num2 from num1
    add al, '0'                       ; Convert result to ASCII
    mov result, al
    jmp display_result

multiplication:
    mov al, num1                      ; Load the first number into AL
    mul num2                          ; Multiply AL by num2 (result in AX)
    aam                               ; Adjust for ASCII output (AH = tens, AL = ones)
    add ax, 3030h                     ; Convert to ASCII
    mov result, ah                    ; Store tens place
    mov result+1, al                  ; Store ones place
    jmp display_result

division:
    cmp num2, 0                       ; Check for division by zero
    je div_by_zero                     ; If zero, jump to error message
    mov al, num1                      ; Load the first number into AL
    mov ah, 0                         ; Clear AH before division
    div num2                          ; Divide AL by num2 (result in AL, remainder in AH)
    add al, '0'                       ; Convert result to ASCII
    mov result, al
    jmp display_result

    ; Handle division by zero
    div_by_zero:
    lea dx, error_msg                 ; Load address of the error message
    mov ah, 9                         ; Display the error message
    int 21h
    jmp exit_program

    ; Display the result
    display_result:
    lea dx, result_msg                ; Load address of the result message
    mov ah, 9                         ; Display the result message
    int 21h
    
    mov dl, result                    ; Load result into DL for output
    cmp operation, '*'                ; Check if multiplication result needs extra print
    je print_multiplication_result
    mov ah, 2                         ; DOS interrupt for displaying a character
    int 21h
    jmp exit_program

print_multiplication_result:
    cmp result, '0'                   ; Check if tens place is zero
    je skip_tens                       ; Skip printing if zero
    mov dl, result                    ; Load tens place into DL
    mov ah, 2                         ; DOS interrupt for displaying a character
    int 21h
skip_tens:
    mov dl, result+1                   ; Load ones place into DL
    mov ah, 2                          ; DOS interrupt for displaying a character
    int 21h

exit_program:
    lea dx, newline                   ; Load address of the newline
    mov ah, 9                         ; Print newline
    int 21h

    ; Exit the program
    mov ah, 4ch                       ; DOS interrupt for program termination
    int 21h
main endp
end main
