import sys
import re
from typing import List, Tuple

Token = Tuple[str, str]

TOKEN_SPECIFICATION = {
	"NUMBER": r"\d+",
	"ID": r"[A-Za-z_][A-Za-z0-9_]*",
	"LE": r"<=",
	"GE": r">=",
	"EQ": r"==",
	"NEQ": r"!=",
	"EQUAL": r"=",
	"PLUS": r"\+",
	"MINUS": r"-",
	"STAR": r"\*",
	"SLASH": r"/",
	"LPARENT": r"\(",
	"RPARENT": r"\)",
	"LBRACE": r"\{",
	"RBRACE": r"\}",
	"LT": r"<",
	"GT": r">",
	"SEMICOLON": r";",
	"COMMA": r",",
	"NEW_LINE": r"\n",
	"MISMATCH": r"."
}

KEYWORDS = [
	"func",
	"if",
	"elseif",
	"else",
	"while",
	"for"
]

TOKEN_REGEX = "|".join(f"(?P<{name}>{pattern})" for name, pattern in TOKEN_SPECIFICATION.items())

class Lexer:
	def __init__(self, code, registers, opcodes):
		self.code = code
		self.registers = registers
		self.opcodes = opcodes

	def tokenize(self) -> List[Token]:
		"""Токенизация"""
		tokens = []

		for match in re.finditer(TOKEN_REGEX, self.code):
			group = match.lastgroup
			value = match.group()

			if value in KEYWORDS:
				tokens.append(("KEYWORD", value))
			elif value in self.opcodes:
				tokens.append(("OPCODE", value))
			elif value in self.registers:
				tokens.append(("REGISTER", value))
			elif group != "MISMATCH":
				tokens.append((group, value))

		return tokens