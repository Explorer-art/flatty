bits 16

push_sum:
push bp
mov bp, sp
push 2
pop ax
pop bp
ret

main:
push bx
mov bx, ax
add bx, 2
push bx
push 1
call push_sum
add sp, 4
pop bx
ret
