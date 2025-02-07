.model small
.stack 100h
.data

logic db 10,13,'and gate $'
logic1 db 10,13,'or gate $'  
logic2 db 10,13,'Xor gate $'  

.code
main proc
    mov ax,@data
    mov ds,ax
    
    mov ah,9
    lea dx,logic
    int 21h
    
    mov bl,111b; oparend1
    and bl,101b; oparend2
    
    add bl,48
    
   
    
    mov ah,2
    mov dl,bl
    int 21h
    
    orgate:
    mov bl,101b   ;
    or bl,101b
    
    add bl,48 
    
    mov ah,9
    lea dx,logic1
    int 21h
    
    mov ah,2
    mov dl,bl
    int 21h 
    
    Xorgate:
    
    mov bl, 101b
    xor bl,100b
    
    add bl,48
    
    mov ah,9
    lea dx, logic2
    int 21h
            
     mov ah,2
    mov dl,bl
    int 21h 
            
    
    exit:
    mov ah,4ch
    int 21h
    
    main endp
end main