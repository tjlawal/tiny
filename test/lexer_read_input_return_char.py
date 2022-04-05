from src.lexer import Lexer

def test_read_input_and_return_char():
  input = "LET foobar = 123"
  lexer = Lexer(input)

  while lexer.peek() != '\0':
    print(lexer.current_char)
    lexer.next_char()

test_read_input_and_return_char()
