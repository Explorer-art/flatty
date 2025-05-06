from typing import List

class ASTNode:
	pass

class Expression(ASTNode):
	pass

class Program(ASTNode):
	"""Программа"""
	def __init__(self, functions: List):
		self.functions = functions

	def __repr__(self):
		return f"Program {{{", ".join(str(func) for func in self.functions)}}}"

class Func(ASTNode):
	"""Определение функции"""
	def __init__(self, identifier: str, args: List, body: List):
		self.identifier = identifier
		self.args = args
		self.body = body

	def __repr__(self):
		return f"Func {self.identifier} ({", ".join(self.args)}) {{{", ".join(str(opcode) for opcode in self.body)}}}"

class CallFunc(ASTNode):
	"""Вызов функции"""
	def __init__(self, func: str, args: List):
		self.func = func
		self.args = args

	def __repr__(self):
		return f"{self.func}({", ".join(str(arg) for arg in self.args)})"

class Register(ASTNode):
	"""Регистр"""
	def __init__(self, register_name: str):
		self.register_name = register_name

	def __repr__(self):
		return f"{self.register_name}"

class Literal(ASTNode):
	"""Литерал. Нужен для представления константных значений"""
	def __init__(self, value: str):
		self.value = value

	def __repr__(self):
		return f"{self.value}"

class Instruction(ASTNode):
	"""Инструкция ассемблера"""
	def __init__(self, opcode: str, operands: List):
		self.opcode = opcode
		self.operands = operands

	def __repr__(self):
		return f"{self.opcode} {", ".join(str(operand) for operand in self.operands)}"

class BinaryOperation(Expression):
	"""Операция с бинарным оператором с 2 операндами"""
	def __init__(self, left: ASTNode, right: ASTNode, operation: str):
		self.left = left
		self.right = right
		self.operation = operation

	def __repr__(self):
		return f"{self.left} {self.operation} {self.right}"

class TernaryOperation(Expression):
	"""Тернарная операция с 1 операндом"""
	def __init__(self, operand: ASTNode, operation: str):
		self.operand = operand
		self.operation = operation

	def __repr__(self):
		return f"{self.operation}{self.operand}"