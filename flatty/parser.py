import sys
from typing import List

class ASTNode:
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


class Parser(ASTNode):
	def __init__(self, tokens) -> List:
		self.tokens = tokens
		self.pos = 0

	def current(self):
		"""Получить текущий токен"""
		return self.tokens[self.pos] if self.pos < len(self.tokens) else None

	def advance(self):
		"""Следующий токен"""
		self.pos += 1

	def expect(self, token_types: List):
		"""Проверка на соответствие типов"""
		if self.current() and self.current()[0] in token_types:
			return self.current()[1]
		else:
			print(f"Error: expected token type {token_types}")
			sys.exit()

	def parse(self) -> Program:
		"""Парсинг"""
		functions = []

		while self.pos < len(self.tokens):
			group, value = self.current()

			if group == "KEYWORD" and value == "func":
				functions.append(self.parse_func())
			else:
				self.advance()

		return Program(functions)

	def parse_func(self):
		"""Парсинг функции"""
		self.advance()
		identifier = self.expect(["ID"])
		self.advance()

		args = self.parse_func_args()
		body = self.parse_func_body()

		return Func(identifier, args, body)

	def parse_func_args(self):
		"""Парсинг параметров функции"""
		self.expect(["LPARENT"])
		self.advance()

		args = []

		while self.current()[0] != "RPARENT":
			if self.current()[0] == "ID":
				args.append(self.current()[1])

			self.advance()

		return args

	def parse_func_body(self):
		"""Парсинг тела функции"""
		self.advance()
		self.expect(["LBRACE"])
		self.advance()

		body = []

		while self.current()[0] != "RBRACE":
			if self.current()[0] == "OPCODE":
				body.append(self.parse_instruction())
			elif self.current()[0] == "ID" and self.tokens[self.pos + 1][0] == "LPARENT":
				body.append(self.parse_call_func())

			self.advance()

		return body

	def parse_instruction(self):
		opcode = self.current()[1]
		self.advance()

		operands = []

		while self.current()[0] != "NEW_LINE":
			if self.current()[0] in "REGISTER NUMBER":
				group, value = self.current()

				if group == "REGISTER":
					operands.append(Register(value))
				elif group == "NUMBER":
					operands.append(Literal(value))

			self.advance()

		return Instruction(opcode, operands)

	def parse_call_func(self):
		func = self.current()[1]
		args = []

		while self.current()[0] != "RPARENT":
			if self.current()[0] in "REGISTER NUMBER":
				group, value = self.current()

				if group == "REGISTER":
					args.append(Register(value))
				elif group == "NUMBER":
					args.append(Literal(value))

			self.advance()

		return CallFunc(func, args)