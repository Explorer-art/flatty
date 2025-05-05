# Flatty
Flatty - это низкоуровневый компилируемый язык программирования общего назначения. Он является упрощенным диалектом ассемблера и реализует множество готовых механизмов таких как переменные, условные операторы, циклы, функции с автоматической передачей параметров через стек и так далее. Код на Flatty транслируется в NASM (для Linux) и в MASM (для Windows).

## Примеры
### Пример 1
```
func sum(a, b) {
	mov ax, a
	add ax, b
}

func main() {
	sum(1, 2)
}
```

### Пример 2
```
func sum(a, b) {
	mov ax, a
	add ax, b
}

func add_sum(a, b) {
	add ax, sum(a, b)	; Операнды как результаты вызова функций
}

func main() {
	add_sum(2, 5)
}
```

### Пример 3
```
func putchar(c) {
	; Вызываем функцию 0Eh прерывания 10h BIOS
	; В al передаем символ

	f"""
	mov ah, 0Eh
	mov al, {c}
	int 10h
	"""
}

func main() {
	putchar('H')
}
```

## Пример 4
```
func set_register(reg, value) {
	mov reg, value
}
```

## Пример 5
```
if (ax > 2) {
	xor ax, ax
}
```