def test_number_token():
  input = "+-123 9.8654*/"
  lexer = Lexer(input)
  token = lexer.get_token()

  while token.kind != TokenType.EOF:
    print(token.kind)
    token = lexer.get_token()

test_number_token()
