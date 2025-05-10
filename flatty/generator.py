import sys
from ast import *

class CodeGenerator:
	def __init__(self, program: Program):
		self.program = program
		self.registers = ["ax", "bx", "cx", "dx"]
		self.code = ""
		self.is_first = False # Флаг для первой обработки выражения
		self.temp_register = None # Временный регистр
		self.current_func = None # Текущая обрабатываемая функция
		self.used_temp_register = False # Флаг использования временного регистра

	def get_parameter_index(self, parameter_name: str, func_node: Func):
		"""Получить индекс параметра в функции"""
		return func_node.params.index(parameter_name)

	def get_free_register(self, expr: Expression, operands_used_registers=None, is_instr=None):
		used_registers = []

		if isinstance(expr, BinaryOperation):
			used_registers = self.get_used_registers(expr.left, used_registers)
			used_registers = self.get_used_registers(expr.right, used_registers)
		elif isinstance(expr, UnaryOperation):
			used_registers = self.get_used_registers(expr.operand, used_registers)

		used_registers += operands_used_registers

		free_registers = [reg for reg in self.registers if reg not in used_registers]

		if free_registers and is_instr:
			if not self.used_temp_register:
				self.used_temp_register = True
				self.code += f"push {free_registers[0]}\n"

			self.temp_register = free_registers[0]

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

	def get_free_register_in_args(self, args):
		used_registers = []

		for arg in args:
			if isinstance(arg, Register):
				used_registers.append(arg.name)
			elif isinstance(arg, BinaryOperation):
				used_registers = self.get_used_registers(arg.left, used_registers)
				used_registers = self.get_used_registers(arg.right, used_registers)
			elif isinstance(arg, UnaryOperation):
				used_registers = self.get_used_registers(arg.operand, used_registers)

		free_registers = [reg for reg in self.registers if reg not in used_registers]

		if free_registers:
			return free_registers[0]

		return None

	def generate(self) -> str:
		"""Генерация кода"""
		for func in self.program.functions:
			self.current_func = func
			self.generate_func(func)

		return self.code

	def generate_func(self, func_node: Func):
		"""Генерация кода функции"""
		self.code += f"{func_node.name}:\n"

		if len(func_node.params) > 0:
			self.code += "push bp\n"
			self.code += "mov bp, sp\n"
		self.generate_func_body(func_node)

		if self.used_temp_register:
			self.code += f"pop {self.temp_register}\n"
			self.used_temp_register = False

		if len(func_node.params) > 0:
			self.code += "pop bp\n"

		self.code += "ret\n\n"

		self.current_func = None

	def generate_func_body(self, func_node: Func):
		"""Генерация кода тела функции"""
		for node in func_node.body:
			if isinstance(node, Instruction):
				self.generate_instruction(node)
			elif isinstance(node, CallFunc):
				self.generate_call_func(node)

	def generate_instruction(self, instruction_node: Instruction):
		"""Генерация кода инструкции"""
		parts = []

		used_registers = []

		for operand in instruction_node.operands:
			if isinstance(operand, Register):
				used_registers.append(operand.name)

		for operand in instruction_node.operands:
			if isinstance(operand, Literal):
				parts.append(operand.value)
			elif isinstance(operand, Register):
				parts.append(operand.name)
			elif isinstance(operand, Parameter):
				# Должно получится [bp + 4] для первого параметра
				# Прибавлять +2 для каждого последующего параметра

				index = self.get_parameter_index(operand.name, self.current_func)
				parts.append(f"[bp + {index * 2 + 6}]")
			elif isinstance(operand, Expression):
				self.is_first = True
				self.used_temp_register = False
				parts.append(str(self.generate_expression(operand, used_registers)))
			else:
				print(f"error: unsupported operand type: {type(operand)}")
				sys.exit()

		self.code += f"{instruction_node.opcode} {', '.join(parts)}\n"

	def generate_expression(self, expr: Expression, used_registers=None):
		"""Генерация кода выражения"""
		result = None

		if isinstance(expr, BinaryOperation):
			left = self.generate_expression(expr.left, used_registers)
			right = self.generate_expression(expr.right, used_registers)

			if expr.operation == "+":
				temp_reg = self.get_free_register(expr, used_registers, True)

				if self.is_first:
					self.is_first = False
					self.code += f"mov {temp_reg}, {left}\n"

				self.code += f"add {temp_reg}, {right}\n"
				return temp_reg
			elif expr.operation == "-":
				temp_reg = self.get_free_register(expr, used_registers, True)

				if self.is_first:
					self.is_first = False
					self.code += f"mov {temp_reg}, {left}\n"

				self.code += f"sub {temp_reg}, {right}\n"
				return temp_reg
		elif isinstance(expr, UnaryOperation):
			operand = self.generate_expression(expr.operand, used_registers)

			if expr.operation == "++":
				if expr.type == "prefix":
					self.code += f"inc {operand}"
					return operand
				elif expr.type == "postfix":
					temp_reg = self.get_free_register(expr, used_registers, True)

					self.code += f"mov {temp_reg}, {operand}\n"
					self.code += f"inc {operand}"
					return temp_reg
			elif expr.operation == "--":
				if expr.type == "prefix":
					self.code += f"dec {operand}"
					return operand
				elif expr.type == "postfix":
					temp_reg = self.get_free_register(expr, used_registers, True)

					self.code += f"mov {temp_reg}, {operand}\n"
					self.code += f"dec {operand}"
					return temp_reg
		elif isinstance(expr, Literal):
			return str(expr.value)
		elif isinstance(expr, Register):
			return str(expr.name)
		elif isinstance(expr, Parameter):
			index = self.get_parameter_index(expr.name, self.current_func)
			return f"[bp + {index * 2 + 6}]"
		else:
			print(f"error: unsupported expression type: {type(expr)}")
			sys.exit()

	def generate_call_func(self, call_func_node: CallFunc) -> str:
		"""Генерация кода вызова функции"""
		if call_func_node.args:
			temp_reg = self.get_free_register_in_args(call_func_node.args)
			self.code += f"push {temp_reg}\n"

			for arg in reversed(call_func_node.args):
				if isinstance(arg, Literal):
					self.code += f"mov {temp_reg}, {arg.value}\n"
					self.code += f"push {temp_reg}\n"

		self.code += f"call {call_func_node.func_name}\n"

		if call_func_node.args:
			self.code += f"add sp, {len(call_func_node.args) * 2}\n"
			self.code += f"pop {temp_reg}\n"