## Идея для оптимизатора
Если результат функции передаётся в ax, то есть например `mov ax, get_ax()`, то можно удалить эту инструкцию так как она не имеет смысла.

```
func push_sum(a, b) {
	mov ax, get_ax()
	add ax, b
}
```

```
push_sum:
push bp
mov bp, sp
call get_ax
mov ax, ax
add ax, [bp + 8]
pop bp
ret
```