import sys
from enum import Enum as enum

class TokenType(enum):
  EOF = -1
  NEWLINE = 0
  NUMBER = 1
  IDENT = 2
  STRING = 3
  # Keywords
  LABEL = 101
  GOTO = 102
  PRINT = 103
  INPUT = 104
  LET = 105
  IF = 106
  THEN = 107
  ENDIF = 108
  WHILE = 109
  REPEAT = 110
  ENDWHILE = 111
  #Operators
  EQ = 201
  EQEQ = 206
  NOTEQ = 207
  LT = 208
  LTEQ = 209
  GT = 210
  GTEQ = 211
  PLUS = 202
  MINUS = 203
  ASTERISK = 204
  SLASH = 205

# TODO(tijani): add DECIMAL as a token KEYWORD.
class Lexer:
  def __init__(self, input):
    self.source = input + '\n'  # source code to lex as a string, append a new line to simplify lexing/parsing the last token/statement
    self.current_char = ''  # current character in the string.
    self.current_position = -1  # cursor position in the string.
    self.next_char()

  # process the next character.
  def next_char(self):
    self.current_position += 1
    if self.current_position >= len(self.source):
      self.current_char = '\0'  # EOF
    else:
      self.current_char = self.source[self.current_position]

  # return the lookahead character.
  def peek(self):
    if self.current_position + 1 >= len(self.source):
      return '\0'
    return self.source[self.current_position + 1]  # return the next character

  # skip withspace except the newlines, which we will use to indicate the end of a statement.
  def skip_whitespace(self):
    while (self.current_char == ' ' or self.current_char == '\t'
           or self.current_char == '\r'):
      self.next_char()

  # skip comments in the code.
  def skip_comment(self):
    if self.current_char == '#':
      while self.current_char != '\n':
        self.next_char()

  # invalid token found, print error message and exit
  def abort(self, message):
    sys.exit("Lexing error: " + message)

  # return the next token
  def get_token(self):
    self.skip_whitespace()
    self.skip_comment()

    token = None  # to prevent UnboundLocalError with python interpreter
    # check the first character of this token to see if we can decide what it is.
    # if it is a multiple character operator (e.g., !=), number, identifier, or keyword
    # then it will process the rest.
    if self.current_char == '+':  # plus token
      token = Token(self.current_char, TokenType.PLUS)
    elif self.current_char == '-':  # minus token
      token = Token(self.current_char, TokenType.MINUS)
    elif self.current_char == '*':  # asterik token
      token = Token(self.current_char, TokenType.ASTERISK)
    elif self.current_char == '/':  # slash token
      token = Token(self.current_char, TokenType.SLASH)
    elif self.current_char == '=':
      # check whether it is a = or ==
      if self.peek() == '=':
        last_char = self.current_char
        self.next_char()
        token = Token(last_char + self.current_char, TokenType.EQEQ)
      else:
        token = Token(self.current_char, TokenType.EQ)
    elif self.current_char == '>':
      # check whether this token is > or >=
      if self.peek() == '=':
        last_char = self.current_char
        self.next_char()
        token = Token(last_char + self.current_char, TokenType.GTEQ)
      else:
        token = Token(self.current_char, TokenType.GT)
    elif self.current_char == '<':
      #check whether this token is < or <=
      if self.peek() == '=':
        last_char = self.current_char
        self.next_char()
        token = Token(last_char + self.current_char, TokenType.LTEQ)
      else:
        token = Token(self.current_char, TokenType.LT)
    elif self.current_char == '!':
      # check if this token is ! or !=
      if self.peek() == '=':
        last_char = self.current_char
        self.next_char()
        token = Token(last_char + self.current_char, TokenType.NOTEQ)
      else:
        self.abort("Expected !=, got !" + self.peek())

    elif self.current_char == '\"':
      # get characters between quotations
      self.next_char()
      start_position = self.current_position

      while self.current_char != '\"':
        # don't allow special characters in the string.
        # No escape characters, newlines, tabs, or %.
        # C's printf will be used on this string.
        if self.current_char == '\r' or self.current_char == '\n' or self.current_char == '\t' or self.current_char == '\\' or self.current_char == '%':
          self.abort("Illegal character in string.")
        self.next_char()

      token_text = self.source[start_position:
                               self.current_position]  # get substring
      token = Token(token_text, TokenType.STRING)

    elif self.current_char.isdigit():
      # leading character is a digit, so this must be a number.
      # get all consecutive digits and decimal if there is one.
      start_position = self.current_position
      while self.peek().isdigit():
        self.next_char()
      if self.peek() == '.':  # we got a Decimal in here!
        self.next_char()

        # decimal must have at least one digit after it.
        if not self.peek().isdigit():
          self.abort("Illegal character in number.")
        while self.peek().isdigit():
          self.next_char()
      token_text = self.source[start_position:self.current_position +
                               1]  # get substring
      token = Token(token_text, TokenType.NUMBER)

    elif self.current_char.isalpha():
      # leading character is a letter, so this must be an identifier or a keyword.
      # get all consecutive alpha numeric characters.
      start_position = self.current_position
      while self.peek().isalnum():
        self.next_char()

      # check if the token is in the list of keywords.
      token_text = self.source[start_position:self.current_position +
                               1]  # get the substring
      keyword = Token.check_if_keyword(token_text)
      if keyword == None:  # Identifier
        token = Token(token_text, TokenType.IDENT)
      else:
        token = Token(token_text, keyword)
    elif self.current_char == '\n':  # newline token
      token = Token(self.current_char, TokenType.NEWLINE)
    elif self.current_char == '\0':  # EOF token
      token = Token('', TokenType.EOF)
    else:
      # unknown token
      self.abort("Unknown token: " + self.current_char)

    self.next_char()
    return token

# Token contains the original text and the type of token.
class Token:
  def __init__(self, token_text, token_kind):
    self.text = token_text  # the token actual text, used for identifiers, strings and enumbers.
    self.kind = token_kind  # the type of token it is classified as.

  @staticmethod
  def check_if_keyword(token_text):
    for kind in TokenType:
      # Relies on all keyword enum values being 1XX.
      if kind.name == token_text and kind.value >= 100 and kind.value < 200:
        return kind
    return None
