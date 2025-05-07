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
	def __init__(self, identifier: str, param: List, body: List):
		self.identifier = identifier
		self.param = param
		self.body = body

	def __repr__(self):
		return f"Func {self.identifier} ({", ".join(self.param)}) {{{", ".join(str(node) for node in self.body)}}}"

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

class Parameter(ASTNode):
	"""Параметр функции"""
	def __init__(self, parameter: str):
		self.parameter = parameter

	def __repr__(self):
		return f"{self.parameter}"

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
		return f"({self.left} {self.operation} {self.right})"

class TernaryOperation(Expression):
	"""Тернарная операция с 1 операндом"""
	def __init__(self, operand: ASTNode, operation: str, type: str):
		self.operand = operand
		self.operation = operation
		self.type = type

	def __repr__(self):
		if self.type == "prefix":
			return f"({self.operation}{self.operand})"
		elif self.type == "postfix":
			return f"({self.operand}{self.operation})"

class IfOperator(ASTNode):
	"""Условный оператор if"""
	def __init__(self, condition: Expression, body: List):
		self.condition = condition
		self.body = body

	def __repr__(self):
		return f"if ({self.condition}) {{{", ".join(str(node) for node in self.body)}}}"

class ElseIfOperator(ASTNode):
	"""Условный оператор elseif"""
	def __init__(self, condition: Expression, body: List):
		self.condition = condition
		self.body = body

	def __repr__(self):
		return f"elseif ({self.condition}) {{{", ".join(str(node) for node in self.body)}}}"

class ElseOperator(ASTNode):
	"""Условный оператор else"""
	def __init__(self, body: List):
		self.body = body

	def __repr__(self):
		return f"else {{{", ".join(str(node) for node in self.body)}}}"

class IfElseChain(ASTNode):
	"""Полная конструкция if / elseif / else"""
	def __init__(self, if_branch: IfOperator, elseif_branches: List[ElseIfOperator] = None, else_branch: ElseOperator = None):
		self.if_branch = if_branch
		self.elseif_branches = elseif_branches
		self.else_branch = else_branch

	def __repr__(self):
		parts = [str(self.if_branch)]
		parts += [str(elseif_op) for elseif_op in self.elseif_branches]

		if self.else_branch:
			parts.append(str(self.else_branch))

		return f" ".join(parts)

class WhileDoLoop(ASTNode):
	def __init__(self, condition: Expression, body: List):
		self.condition = condition
		self.body = body

	def __repr__(self):
		return f"while ({self.condition}) {{{", ".join(str(node) for node in self.body)}}}"

class DoWhileLoop(ASTNode):
	def __init__(self, condition: Expression, body: List):
		self.condition = condition
		self.body = body

	def __repr__(self):
		return f"{{{", ".join(str(node) for node in self.body)}}} while ({self.condition})"

class ForLoop(ASTNode):
	def __init__(self, counter, condition: Expression, operation: Expression, body: List):
		self.counter = counter
		self.condition = condition
		self.operation = operation
		self.body = body

	def __repr__(self):
		return f"for ({self.counter}; {self.condition}; {self.operation}) {{{", ".join(str(node) for node in self.body)}}}"