.model small
.stack 100h
.data
    msg1 db 'Enter daddy bitch number: $'   ; Message to prompt for the first number
    msg2 db 'Enter second number: $'  ; Message to prompt for the second number
    result_msg db 'Result: $'         ; Message to display the result
    newline db 13, 10, '$'            ; Carriage return and line feed for new line
    num1 db ?                         ; Variable to store the first number
    num2 db ?                         ; Variable to store the second number
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

    ; Prompt for the second number
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

    ; Subtract the two numbers
    mov al, num1                      ; Load the first number into AL
    sub al, num2                      ; Subtract num2 from num1
    add al, '0'                       ; Convert result to ASCII
    mov result, al                    ; Store the result

    ; Display the result
    lea dx, result_msg                ; Load address of the result message
    mov ah, 9                         ; Display the result message
    int 21h
    
    mov dl, result                    ; Load result into DL for output
    mov ah, 2                         ; DOS interrupt for displaying a character
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
