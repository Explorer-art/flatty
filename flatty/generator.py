import sys
from ast import *

class CodeGenerator:
	def __init__(self, program: Program):
		self.program = program
		self.registers = ["ax", "bx", "cx", "dx"]
		self.code = ""
		self.is_first = False # Флаг для первой обработки выражения

	def get_parameter_index(self, parameter_name: str, func_node: Func):
		"""Получить индекс параметра в функции"""
		return func_node.params.index(parameter_name)

	def get_free_register(self, expr: Expression):
		used_registers = []

		if isinstance(expr, BinaryOperation):
			used_registers = self.get_used_registers(expr.left, used_registers)
			used_registers = self.get_used_registers(expr.right, used_registers)
		elif isinstance(expr, UnaryOperation):
			used_registers = self.get_used_registers(expr.operand, used_registers)

		free_registers = [reg for reg in self.registers if reg not in used_registers]

		if free_registers:
			return free_registers[0]

		return None

	def get_used_registers(self, expr, used_registers):
		if isinstance(expr, BinaryOperation):
			used_registers = self.get_used_registers(expr.left, used_registers)
			used_registers = self.get_used_registers(expr.right, used_registers)
		elif isinstance(expr, UnaryOperation):
			used_registers = self.get_used_registers(expr.operand, used_registers)
		elif isinstance(expr, Register):
			used_registers.append(expr.name)

		return used_registers

	def generate(self) -> str:
		"""Генерация кода"""
		for func in self.program.functions:
			self.generate_func(func)

		return self.code

	def generate_func(self, func_node: Func):
		"""Генерация кода функции"""
		self.code += f"{func_node.name}:\n"

		if len(func_node.params) > 0:
			self.code += "push bp\n"
			self.code += "mov bp, sp\n"
		self.generate_func_body(func_node)

		if len(func_node.params) > 0:
			self.code += "pop bp\n"

		self.code += "ret\n"

	def generate_func_body(self, func_node: Func):
		"""Генерация кода тела функции"""
		for node in func_node.body:
			if isinstance(node, Instruction):
				self.generate_instruction(node)

	def generate_instruction(self, instruction_node: Instruction):
		"""Генерация кода инструкции"""
		parts = []

		for operand in instruction_node.operands:
			if isinstance(operand, Literal):
				parts.append(operand.value)
			elif isinstance(operand, Register):
				parts.append(operand.name)
			elif isinstance(operand, Parameter):
				# Должно получится [bp + 4] для первого параметра
				# Прибавлять +2 для каждого последующего параметра

				index = self.get_parameter_index(operand.name)
				parts.append(f"[bp + {index * 2 + 4}]")
			elif isinstance(operand, Expression):
				self.is_first = True
				parts.append(str(self.generate_expression(operand)))
			else:
				print(f"error: unsupported operand type: {type(operand)}")
				sys.exit()

		self.code += f"{instruction_node.opcode} {', '.join(parts)}\n"

	def generate_expression(self, expr: Expression):
		"""Генерация кода выражения"""
		result = None

		if isinstance(expr, BinaryOperation):
			left = self.generate_expression(expr.left)
			right = self.generate_expression(expr.right)

			if expr.operation == "+":
				temp_reg = self.get_free_register(expr)

				if self.is_first:
					self.is_first = False
					self.code += f"mov {temp_reg}, {left}\n"

				self.code += f"add {temp_reg}, {right}\n"
				return temp_reg
			elif expr.operation == "-":
				temp_reg = self.get_free_register(expr)

				if self.is_first:
					self.is_first = False
					self.code += f"mov {temp_reg}, {left}\n"

				self.code += f"sub {temp_reg}, {right}\n"
				return temp_reg
		elif isinstance(expr, UnaryOperation):
			operand = self.generate_expression(expr.operand)

			if expr.operation == "++":
				if expr.type == "prefix":
					self.code += f"inc {operand}"
					return operand
				elif expr.type == "postfix":
					temp_reg = self.get_free_register(expr)

					self.code += f"mov {temp_reg}, {operand}\n"
					self.code += f"inc {operand}"
					return temp_reg
			elif expr.operation == "--":
				if expr.type == "prefix":
					self.code += f"dec {operand}"
					return operand
				elif expr.type == "postfix":
					temp_reg = self.get_free_register(expr)

					self.code += f"mov {temp_reg}, {operand}\n"
					self.code += f"dec {operand}"
					return temp_reg
		elif isinstance(expr, Literal):
			return str(expr.value)
		elif isinstance(expr, Register):
			return str(expr.name)
		elif isinstance(expr, Parameter):
			index = self.get_parameter_index(expr.name)
			return f"[bp + {index * 2 + 4}]"
		else:
			print(f"error: unsupported expression type: {type(expr)}")
			sys.exit()

	def generate_call_func(self, call_func_node: CallFunc) -> str:
		"""Генерация кода вызова функции"""