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

	def parse_func(self) -> Func:
		"""Парсинг функции"""
		self.advance()
		identifier = self.expect(["ID"])
		self.advance()

		args = self.parse_func_args()
		self.advance()
		body = self.parse_func_body()

		return Func(identifier, args, body)

	def parse_func_args(self) -> List:
		"""Парсинг параметров функции"""
		self.expect(["LPARENT"])
		self.advance()

		args = []

		while self.current()[0] != "RPARENT":
			if self.current()[0] == "ID":
				args.append(self.current()[1])

			self.advance()

		return args

	def parse_func_body(self) -> List:
		"""Парсинг тела функции"""
		self.expect(["LBRACE"])
		self.advance()

		body = []

		while self.current()[0] != "RBRACE":
			group, value = self.current()
			if group == "OPCODE":
				body.append(self.parse_instruction())
			elif group == "ID" and self.tokens[self.pos + 1][0] == "LPARENT":
				body.append(self.parse_call_func())
			elif group == "KEYWORD" and value == "if":
				body.append(self.parse_if_else_chain())
			elif group == "KEYWORD" and value == "while":
				body.append(self.parse_while_loop())

			self.advance()

		return body

	def parse_instruction(self) -> Instruction:
		"""Парсинг инструкции"""
		opcode = self.current()[1]
		self.advance()
		operands = self.parse_operands()

		return Instruction(opcode, operands)

	def parse_operands(self) -> List:
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
				for node in self.parse_expr(buffer):
					operands.append(node)

				buffer = []
			else:
				buffer.append(self.current())

			self.advance()

		for node in self.parse_expr(buffer):
			operands.append(node)

		return operands

	def parse_expr(self, buffer) -> List:
		"""Парсинг выражений в буфере"""
		result = []

		for i, node in enumerate(buffer):
			if isinstance(node, tuple):
				if node[0] in "PLUS MINUS STAR SLASH LT GT LE GE EQ NEQ":
					return [BinaryOperation(buffer[i - 1], buffer[i + 1], node[1])]
			else:
				result.append(node)

		return result

	def parse_call_func(self) -> CallFunc:
		"""Парсинг вызова функции"""
		func = self.current()[1]
		self.advance()
		args = self.parse_call_func_args()

		return CallFunc(func, args)

	def parse_call_func_args(self) -> List:
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
				for node in self.parse_expr(buffer):
					args.append(node)

				buffer = []
			else:
				buffer.append(self.current())

			self.advance()

		for node in self.parse_expr(buffer):
			args.append(node)

		return args

	def parse_if_else_chain(self) -> IfElseChain:
		"""Парсинг конструкции if / elseif / else"""
		self.advance()
		conditions = self.parse_conditions()

		self.advance()
		body = self.parse_func_body()
		if_branch = IfOperator(conditions, body)

		self.advance()

		elseif_branches = []

		while self.current() and self.current()[1] == "elseif":
			self.advance()
			conditions = self.parse_conditions()

			self.advance()
			body = self.parse_func_body()
			elseif_branches.append(ElseIfOperator(conditions, body))

		self.advance()

		else_branch = None

		if self.current() and self.current()[1] == "else":
			self.advance()
			body = self.parse_func_body()
			else_branch = ElseOperator(body)

		return IfElseChain(if_branch, elseif_branches, else_branch)

	def parse_conditions(self) -> List:
		"""Парсинг условий"""
		self.expect("LPARENT")
		self.advance()

		conditions = []
		buffer = []

		while self.current()[0] != "RPARENT":
			group, value = self.current()

			if group == "REGISTER":
				buffer.append(Register(value))
			elif group == "NUMBER":
				buffer.append(Literal(value))
			else:
				buffer.append(self.current())

			self.advance()

		for condition in self.parse_expr(buffer):
			conditions.append(condition)

		return conditions

	def parse_while_loop(self) -> WhileLoop:
		"""Парсинг цикла while"""
		self.advance()
		conditions = self.parse_conditions()

		self.advance()
		body = self.parse_func_body()

		return WhileLoop(conditions, body)