bits 16
jmp start
get_bx:
mov ax, bx
ret

set_ax:
push bp
mov bp, sp
mov ax, [bp + 6]
pop bp
ret

push_sum:
push bp
mov bp, sp
call get_bx
push ax
call set_ax
add sp, 2
mov ax, ax
add ax, [bp + 8]
pop bp
ret

start:
push 2
push 1
call push_sum
add sp, 4
cli
hlt
