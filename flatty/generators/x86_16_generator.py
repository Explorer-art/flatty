import sys
from ast import *

class x86_16_CodeGenerator:
	def __init__(self, program: Program):
		self.program = program
		self.registers = ["ax", "bx", "cx", "dx"]
		self.code = ""
		self.is_first = False # Флаг для первой обработки выражения
		self.temp_registers = [] # Стек временных регистров
		self.current_func = None # Текущая обрабатываемая функция

	def get_parameter_index(self, parameter_name: str, func_node: Func):
		"""Получить индекс параметра в функции"""
		return func_node.params.index(parameter_name)

	def get_free_register(self, expr: Expression, operands_used_registers=None):
		"""Добавить свободный регистр в стек self.temp_registers"""
		used_registers = []

		if isinstance(expr, BinaryOperation):
			used_registers = self.get_used_registers(expr.left, used_registers)
			used_registers = self.get_used_registers(expr.right, used_registers)
		elif isinstance(expr, UnaryOperation):
			used_registers = self.get_used_registers(expr.operand, used_registers)

		if operands_used_registers:
			used_registers += operands_used_registers

		free_registers = [reg for reg in self.registers if reg not in used_registers]

		if free_registers:
			self.temp_registers.append(free_registers[0])

	def get_used_registers(self, expr, used_registers):
		"""Получить используемые в выражении регистры"""
		if isinstance(expr, BinaryOperation):
			used_registers = self.get_used_registers(expr.left, used_registers)
			used_registers = self.get_used_registers(expr.right, used_registers)
		elif isinstance(expr, UnaryOperation):
			used_registers = self.get_used_registers(expr.operand, used_registers)
		elif isinstance(expr, Register):
			used_registers.append(expr.name)

		return used_registers

	def get_free_register_in_args(self, args):
		"""
		Добавить свободный регистр из аргументоввызова функции
		в стек self.temp_registers
		"""
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
			self.temp_registers.append(free_registers[0])

	def get_temp_reg(self):
		if not self.temp_registers:
			print("error: not temp register")
			sys.exit()

		return self.temp_registers[-1]

	def push_temp_reg(self):
		if not self.temp_registers:
			print("error: not temp register")
			sys.exit()

		self.code += f"push {self.get_temp_reg()}\n"

	def pop_temp_reg(self):
		if not self.temp_registers:
			print("error: not temp register")
			sys.exit()

		self.code += f"pop {self.get_temp_reg()}\n"

	def generate(self) -> str:
		"""Генерация кода"""
		for func in self.program.functions:
			self.current_func = func
			self.generate_func(func)

		code = "bits 16\n"
		code += "jmp start\n"
		code += self.code

		return code

	def generate_func(self, func_node: Func):
		"""Генерация кода функции"""
		if func_node.name == "main":
			self.code += "start:\n"
		else:
			self.code += f"{func_node.name}:\n"

		if len(func_node.params) > 0:
			self.code += "push bp\n"
			self.code += "mov bp, sp\n"

		self.generate_func_body(func_node)

		if len(func_node.params) > 0:
			self.code += "pop bp\n"

		if func_node.name == "main":
			self.code += "cli\n"
			self.code += "hlt\n"
		else:
			self.code += "ret\n\n"

		self.current_func = None

	def generate_func_body(self, func_node: Func):
		"""Генерация кода тела функции"""
		for node in func_node.body:
			if isinstance(node, Instruction):
				self.generate_instruction(node)
			elif isinstance(node, CallFunc):
				self.is_first = True
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
				self.get_free_register(operand, used_registers)
				self.push_temp_reg()
				parts.append(str(self.generate_expression(operand)))
			else:
				print(f"error: unsupported operand type: {type(operand)}")
				sys.exit()

		self.code += f"{instruction_node.opcode} {', '.join(parts)}\n"

		if self.temp_registers:
			self.pop_temp_reg()
			self.temp_registers.pop() # Удаляем временный регистр

	def generate_expression(self, expr: Expression):
		"""Генерация кода выражения"""
		result = None

		if isinstance(expr, BinaryOperation):
			left = self.generate_expression(expr.left)
			right = self.generate_expression(expr.right)

			if expr.operation == "+":
				if self.is_first:
					self.is_first = False
					self.code += f"mov {self.get_temp_reg()}, {left}\n"

				self.code += f"add {self.get_temp_reg()}, {right}\n"
				result = self.get_temp_reg()
			elif expr.operation == "-":
				if self.is_first:
					self.is_first = False
					self.code += f"mov {self.get_temp_reg()}, {left}\n"

				self.code += f"sub {self.get_temp_reg()}, {right}\n"
				result = self.get_temp_reg()
		elif isinstance(expr, UnaryOperation):
			operand = self.generate_expression(expr.operand)

			if expr.operation == "++":
				if expr.type == "prefix":
					self.code += f"inc {operand}"
					result = operand
				elif expr.type == "postfix":
					self.code += f"mov {self.get_temp_reg()}, {operand}\n"
					self.code += f"inc {operand}"
					result = self.get_temp_reg()
			elif expr.operation == "--":
				if expr.type == "prefix":
					self.code += f"dec {operand}"
					result = operand
				elif expr.type == "postfix":
					self.code += f"mov {self.get_temp_reg()}, {operand}\n"
					self.code += f"dec {operand}"
					result = self.get_temp_reg()
		elif isinstance(expr, Literal):
			result = str(expr.value)
		elif isinstance(expr, Register):
			result = str(expr.name)
		elif isinstance(expr, Parameter):
			index = self.get_parameter_index(expr.name, self.current_func)
			result = f"[bp + {index * 2 + 6}]"
		else:
			print(f"error: unsupported expression type: {type(expr)}")
			sys.exit()

		return result

	def generate_call_func(self, call_func_node: CallFunc) -> str:
		"""Генерация кода вызова функции"""
		if call_func_node.args:
			for arg in reversed(call_func_node.args):
				if isinstance(arg, Literal):
					self.code += f"push {arg.value}\n"
				elif isinstance(arg, Register):
					self.code += f"push {arg.name}\n"
				elif isinstance(arg, Expression):
					self.get_free_register_in_args(call_func_node.args)
					
					if self.is_first:
						self.push_temp_reg()

					self.is_first = True
					self.generate_expression(arg)

					self.push_temp_reg()

		self.code += f"call {call_func_node.func_name}\n"

		if call_func_node.args:
			self.code += f"add sp, {len(call_func_node.args) * 2}\n"

		if self.temp_registers:
			self.pop_temp_reg()
			self.temp_registers.pop()