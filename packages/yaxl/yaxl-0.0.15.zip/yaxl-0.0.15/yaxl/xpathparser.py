def parse_expression(s):
	for char in s:
		if char == '(':
			yield LPAREN