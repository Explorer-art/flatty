bits 16

jmp start

get_bx:
mov ax, bx
ret

start:
call get_bx
mov cx, ax
cli
hlt
