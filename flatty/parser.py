import sys
from typing import List
from ast import *

class ParserError(Exception):
	def __init__(self, message, position=None):
		super().__init__(f"{message} at token position {position}")

class Parser(ASTNode):
	def __init__(self, tokens) -> List:
		self.tokens = tokens
		self.pos = 0
		self.current_func = None

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
			raise ParserError(f"expected token type {token_types}", position=self.pos)

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

		# Если название функции равно опкоду или регистру выдаем ошибку
		if self.current()[0] == "OPCODE" or self.current()[0] == "REGISTER":
			raise ParserError("function name matches the opcode", position=self.pos)

		identifier = self.expect(["ID"])
		self.advance()

		params = self.parse_func_params()
		self.current_func = {"name": identifier, "params": params}

		self.advance()
		body = self.parse_func_body()

		return Func(identifier, params, body)

	def parse_func_params(self) -> List:
		"""Парсинг параметров функции"""
		self.expect(["LPARENT"])
		self.advance()

		params = []

		while self.current()[0] != "RPARENT":
			if self.current()[0] == "ID":
				params.append(self.current()[1])

			self.advance()

		return params

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
				body.append(self.parse_while_do_loop())
			elif group == "LBRACE" and self.tokens[self.pos - 1][0] != "RPARENT":
				body.append(self.parse_do_while_loop())
			elif group == "KEYWORD" and value == "for":
				body.append(self.parse_for_loop())

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
				raise ParserError("expected operand before ','", position=self.pos)

			if group == "REGISTER":
				buffer.append(Register(value))
			elif group == "NUMBER":
				buffer.append(Literal(value))
			elif group == "ID" and self.tokens[self.pos + 1][0] == "LPARENT":
				buffer.append(self.parse_call_func())
			elif group == "ID" and value in self.current_func["params"]:
				buffer.append(Parameter(value))
			elif group == "COMMA":
				operands.append(self.parse_expr(buffer))
				buffer = []
			else:
				buffer.append(self.current())

			self.advance()

		operands.append(self.parse_expr(buffer))

		return operands

	def parse_expr(self, buffer) -> Expression:
		"""Парсинг выражений в буфере"""
		buffer = self.parse_prefix_operation(buffer, ["PLUS"])
		buffer = self.parse_prefix_operation(buffer, ["MINUS"])
		buffer = self.parse_postfix_operation(buffer, ["PLUS"])
		buffer = self.parse_postfix_operation(buffer, ["MINUS"])
		buffer = self.parse_binary_opeartion(buffer, ["STAR", "SLASH"])
		buffer = self.parse_binary_opeartion(buffer, ["PLUS", "MINUS"])
		buffer = self.parse_binary_opeartion(buffer, ["LT", "GT", "LE", "GE", "EQ", "NEQ"])
		buffer = self.parse_binary_opeartion(buffer, ["EQUAL"])

		return buffer[0] if buffer else None

	def parse_prefix_operation(self, buffer, operations):
		"""Парсинг префиксных операций в выражении"""
		result = []
		i = 0

		while i < len(buffer):
			if (i + 2 < len(buffer)
				and isinstance(buffer[i], tuple)
				and buffer[i][0] in operations
				and isinstance(buffer[i + 1], tuple)
				and buffer[i + 1][0] in operations
			):
				result.append(UnaryOperation(buffer[i + 2], str(buffer[i][1]) + str(buffer[i + 1][1]), "prefix"))

				i += 3
			else:
				result.append(buffer[i])
				i += 1

		return result

	def parse_postfix_operation(self, buffer, operations):
		"""Парсинг постфиксных операций в выражении"""
		result = []
		i = 0

		while i < len(buffer):
			if (i + 1 < len(buffer)
				and isinstance(buffer[i], tuple)
				and buffer[i][0] in operations
				and isinstance(buffer[i + 1], tuple)
				and buffer[i + 1][0] in operations
			):
				operand = result.pop()

				result.append(UnaryOperation(operand, str(buffer[i][1]) + str(buffer[i + 1][1]), "postfix"))

				i += 2
			else:
				result.append(buffer[i])
				i += 1

		return result

	def parse_binary_opeartion(self, buffer, operations):
		"""Парсинг бинарных операций в выражении"""
		result = []
		i = 0

		while i < len(buffer):
			node = buffer[i]

			if isinstance(node, tuple) and node[0] in operations:
				left = result.pop()
				right = buffer[i + 1]

				result.append(BinaryOperation(left, right, node[1]))

				i += 2
			else:
				result.append(node)
				i += 1

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
		self.advance()

		while self.current()[0] != "RPARENT":
			group, value = self.current()

			if group == "REGISTER":
				buffer.append(Register(value))
			elif group == "NUMBER":
				buffer.append(Literal(value))
			elif group == "ID" and self.tokens[self.pos + 1][0] == "LPARENT":
				buffer.append(self.parse_call_func())
			elif group == "COMMA":
				args.append(self.parse_expr(buffer))

				buffer = []
			else:
				buffer.append(self.current())

			self.advance()

		arg = self.parse_expr(buffer)

		if arg:
			args.append(arg)

		return args

	def parse_if_else_chain(self) -> IfElseChain:
		"""Парсинг конструкции if / elseif / else"""
		self.advance()
		condition = self.parse_condition()

		self.advance()
		body = self.parse_func_body()
		if_branch = IfOperator(condition, body)

		self.advance()

		elseif_branches = []

		while self.current() and self.current()[1] == "elseif":
			self.advance()
			condition = self.parse_condition()

			self.advance()
			body = self.parse_func_body()
			elseif_branches.append(ElseIfOperator(condition, body))

		self.advance()

		else_branch = None

		if self.current() and self.current()[1] == "else":
			self.advance()
			body = self.parse_func_body()
			else_branch = ElseOperator(body)

		return IfElseChain(if_branch, elseif_branches, else_branch)

	def parse_condition(self) -> Expression:
		"""Парсинг условий"""
		self.expect("LPARENT")
		self.advance()

		buffer = []

		while self.current()[0] != "RPARENT":
			group, value = self.current()

			if group == "REGISTER":
				buffer.append(Register(value))
			elif group == "NUMBER":
				buffer.append(Literal(value))
			elif group == "ID" and self.tokens[self.pos + 1][0] == "LPARENT":
				buffer.append(self.parse_call_func())
			elif group == "ID" and value in self.current_func["params"]:
				buffer.append(Parameter(value))
			else:
				buffer.append(self.current())

			self.advance()

		return self.parse_expr(buffer)

	def parse_while_do_loop(self) -> WhileDoLoop:
		"""Парсинг цикла while"""
		self.advance()
		condition = self.parse_condition()

		self.advance()
		body = self.parse_func_body()

		return WhileDoLoop(condition, body)

	def parse_do_while_loop(self) -> DoWhileLoop:
		"""Парсинг цикла do while"""
		body = self.parse_func_body()

		self.advance()

		if self.current()[1] != "while":
			raise ParserError("expected keyword 'while' after '}'", position=self.pos)

		self.advance()
		condition = self.parse_condition()

		return DoWhileLoop(condition, body)

	def parse_for_loop(self) -> ForLoop:
		"""Парсинг цикла for"""
		self.advance()
		counter, condition, operation = self.parse_for_init()
		body = self.parse_func_body()

		return ForLoop(counter, condition, operation, body)

	def parse_for_init(self):
		"""Парсинг блока инициализации цикла for"""
		self.expect("LPARENT")
		self.advance()

		counter = None
		condition = None
		operation = None

		buffer = []
		count_semicolon = 0

		while self.current()[0] != "RPARENT":
			group, value = self.current()

			if group == "SEMICOLON" and len(buffer) == 0:
				raise ParserError("expected for init before ';'", position=self.pos)

			if group == "REGISTER":
				buffer.append(Register(value))
			elif group == "NUMBER":
				buffer.append(Literal(value))
			elif group == "ID" and self.tokens[self.pos + 1][0] == "LPARENT":
				buffer.append(self.parse_call_func())
			elif group == "ID" and value in self.current_func["params"]:
				buffer.append(Parameter(value))
			elif group == "SEMICOLON":
				count_semicolon += 1

				if count_semicolon == 1:
					counter = self.parse_expr(buffer)
				elif count_semicolon == 2:
					condition = self.parse_expr(buffer)

				buffer = []
			else:
				buffer.append(self.current())

			self.advance()

		operation = self.parse_expr(buffer)
		self.advance()

		return counter, condition, operation