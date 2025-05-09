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

OPCODES = [
	"mov",
	"add",
	"sub",
	"mul",
	"inc",
	"dec",
	"xor"
]

REGISTERS = [
	"ax",
	"bx",
	"cx",
	"dx",
	"al",
	"bl",
	"cl",
	"dl",
	"ah",
	"bh",
	"ch",
	"dh"
]

TOKEN_REGEX = "|".join(f"(?P<{name}>{pattern})" for name, pattern in TOKEN_SPECIFICATION.items())

class Lexer:
	def __init__(self, code):
		self.code = code

	def tokenize(self) -> List[Token]:
		"""Токенизация"""
		tokens = []

		for match in re.finditer(TOKEN_REGEX, self.code):
			group = match.lastgroup
			value = match.group()

			if value in KEYWORDS:
				tokens.append(("KEYWORD", value))
			elif value in OPCODES:
				tokens.append(("OPCODE", value))
			elif value in REGISTERS:
				tokens.append(("REGISTER", value))
			elif group != "MISMATCH":
				tokens.append((group, value))

		return tokens