import sys
from typing import List
from ast import *

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
		"""Парсинг инструкции"""
		opcode = self.current()[1]
		self.advance()
		operands = self.parse_operands()
		# print(operands)

		return Instruction(opcode, operands)

	def parse_operands(self):
		"""Парсинг операндов"""
		operands = []
		buffer = []

		while self.current()[0] != "NEW_LINE":
			group, value = self.current()

			if group == "COMMA" and len(buffer) == 0:
				print("Syntax error")
				sys.exit()

			if group == "REGISTER":
				buffer.append(Register(value))
			elif group == "NUMBER":
				buffer.append(Literal(value))
			elif group == "COMMA":
				for node in self.parse_buffer(buffer):
					operands.append(node)

				buffer = []
			else:
				buffer.append(self.current())

			self.advance()

		for node in self.parse_buffer(buffer):
			operands.append(node)

		return operands

	def parse_buffer(self, buffer):
		"""Парсинг выражений в буфере"""
		result = []

		for i, node in enumerate(buffer):
			print(node)
			if isinstance(node, tuple):
				if node[0] == "PLUS" or node[0] == "MINUS" or node[0] == "STAR" or node[0] == "SLASH":
					return [BinaryOperation(buffer[i - 1], buffer[i + 1], node[1])]
			else:
				result.append(node)

		return result

	def parse_call_func(self):
		"""Парсинг вызова функции"""
		func = self.current()[1]
		self.advance()
		args = self.parse_call_func_args()

		return CallFunc(func, args)

	def parse_call_func_args(self):
		"""Парсинг параметров вызываемой функции"""
		args = []
		buffer = []

		self.expect("LPARENT")

		while self.current()[0] != "RPARENT":
			group, value = self.current()

			if group == "REGISTER":
				buffer.append(Register(value))
			elif group == "NUMBER":
				buffer.append(Literal(value))
			elif group == "COMMA":
				print("Clear", buffer)

				for node in self.parse_buffer(buffer):
					args.append(node)

				buffer = []
			else:
				buffer.append(self.current())

			self.advance()

		for node in self.parse_buffer(buffer):
			args.append(node)

		return args