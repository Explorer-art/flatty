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
	add ax, sum(a, b)	// Операнды как результаты вызова функций
}

func main() {
	add_sum(2, 5)
}
```

### Пример 3
```
func putchar(c) {
	// Вызываем функцию 0Eh прерывания 10h BIOS
	// В al передаем символ

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

## Пример 6
```
func set_ax () {
	mov ax, 1 * 2 + 5 > 10
}

func main() {
	while (ax > 2 + 2 * 2) {
		set_ax()
	}
}
```

## Пример 7
```
func set_ax () {
	mov ax, 1 * 2 + 5 > 10
}

func main() {
	{
		set_ax()
	} while (ax > 2 + 2 * 2)
}
```

## Пример 8
```
func set_ax () {
	mov ax, 1 * 2 + 5 > 10
}

func main() {
	for (cx = 0; cx > 10; cx++) {
		set_ax()
	}
}
```

## Пример 9
Программа которая считает сумму чисел от 1 до 10
```
func sum(a, b) {
	mov ax, a
	add ax, b
}

func main() {
	mov cx, 1
	mov bx, 0

	while (cx <= 10) {
		sum(bx, cx)
		mov bx, ax
		inc cx
	}

	mov ax, bx
}
```

## Пример 10
Программа которая ищет максимум из трёх чисел
```
func max(a, b) {
	if (a > b) {
		mov ax, a
	} else {
		mov ax, b
	}
}

func main() {
	mov bx, 5
	mov cx, 8
	mov dx, 3

	max(bx, cx)		// ax = max(bx, cx)
	max(ax, dx)		// ax = max(ax, dx)

	// В результате в ax будет максимум из трёх чисел
}
```