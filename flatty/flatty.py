import os
import sys
import argparse
from preprocessor import Preprocessor
from lexer import Lexer
from parser import Parser

DEBUG = True

def compile(code, flags):
	# Препроцессинг
	preprocessor = Preprocessor(code)
	code = preprocessor.preprocess()

	if DEBUG:
		print("Preprocessor:")
		print(code)
		print("")

	# Токенизация
	lexer = Lexer(code)
	tokens = lexer.tokenize()

	if DEBUG:
		print("Tokens:")
		print(tokens)
		print("")

	# Парсинг
	parser = Parser(tokens)
	ast = parser.parse()

	if DEBUG:
		print("AST:")
		print(ast)
		print("")

if __name__ == "__main__":
	argument_parser = argparse.ArgumentParser()

	argument_parser.add_argument("input_file", type=str, help="Input file")
	argument_parser.add_argument("-o", "--output-file", type=str, default="out.asm", help="Output file")

	args = argument_parser.parse_args()

	if not os.path.exists(args.input_file):
		print(f"Error: file {args.input_file} not exists")
		sys.exit()

	with open(args.input_file, "r") as file:
		code = file.read()

	compile(code, args)