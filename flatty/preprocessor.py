import re

class Preprocessor:
	def __init__(self, code):
		self.code = code

	def preprocess(self) -> str:
		"""Препроцессинг"""
		processed_code = ""
		lines = self.code.split("\n")

		# Удаляем все комментарии и удалеяем лишние пробелы
		for line in lines:
			comment_index = line.find(";")

			if comment_index != -1:
				line = line[:comment_index].rstrip()

			if line.strip():
				processed_code += line + "\n"

		return processed_code