REGISTERS = frozenset([
	"ax", "bx", "cx", "dx",
	"al", "bl", "cl", "dl",
	"ah", "bh", "ch", "dh",
	"di", "si", "bp", "sp"
])

OPCODES = frozenset([
	"mov",
	"add",
	"sub",
	"mul",
	"inc",
	"dec",
	"xor",
	"push",
	"pop"
])