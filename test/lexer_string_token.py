def test_string_token():
  input = "+- \"This is a string\" # This is a comment!\n */"
  lexer = Lexer(input)
  token = lexer.get_token()

  while token.kind != TokenType.EOF:
    print(token.kind)
    token = lexer.get_token()

test_string_token()
