import sys
from ast import *

class RealModeGenerator:
	def __init__(self, program: Program):
		self.program = program
		self.code = ""
		self.current_func = None # Текущая обрабатываемая функция

	def get_parameter_index(self, parameter_name: str, func_node: Func):
		"""Получить индекс параметра в функции"""
		return func_node.params.index(parameter_name)

	def generate(self) -> str:
		"""Генерация кода"""
		for func in self.program.functions:
			self.current_func = func
			self.generate_func(func)

		code = "bits 16\n\n"
		code += "jmp start\n\n"
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
				self.generate_call_func(node)

	def generate_instruction(self, instruction: Instruction):
		"""Генерация кода инструкции"""
		parts = []

		used_registers = []

		for operand in instruction.operands:
			if isinstance(operand, Register):
				used_registers.append(operand.name)

		for operand in instruction.operands:
			if isinstance(operand, Literal):
				parts.append(operand.value)
			elif isinstance(operand, Register):
				parts.append(operand.name)
			elif isinstance(operand, Parameter):
				# Должно получится [bp + 4] для первого параметра
				# Прибавлять +2 для каждого последующего параметра

				index = self.get_parameter_index(operand.name, self.current_func)
				parts.append(f"[bp + {index * 2 + 6}]")
			elif isinstance(operand, CallFunc):
				self.generate_call_func(operand)
				parts.append("ax") # Результат функции возвращается в регистре AX
			else:
				print(f"error: unsupported operand type: {type(operand)}")
				sys.exit()

		self.code += f"{instruction.opcode} {', '.join(parts)}\n"

	def generate_call_func(self, call_func_node: CallFunc) -> str:
		"""Генерация кода вызова функции"""
		if call_func_node.args:
			for arg in reversed(call_func_node.args):
				if isinstance(arg, Literal):
					self.code += f"push {arg.value}\n"
				elif isinstance(arg, Register):
					self.code += f"push {arg.name}\n"
				elif isinstance(arg, CallFunc):
					self.generate_call_func(arg)
					self.code += "push ax\n"

		self.code += f"call {call_func_node.func_name}\n"

		if call_func_node.args:
			self.code += f"add sp, {len(call_func_node.args) * 2}\n"