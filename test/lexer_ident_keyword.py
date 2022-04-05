from

def test_ident_and_keywords():
  input = "IF+-123 foo*THEN/"
  lexer = Lexer(input)
  token = lexer.get_token()

  while token.kind != TokenType.EOF:
    print(token.kind)
    token = lexer.get_token()

test_ident_and_keywords()
