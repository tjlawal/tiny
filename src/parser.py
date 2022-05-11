import sys
from lexer import *
from emitter import *

# Pareser object keeps track of current token and checks if the code matches the grammar.
class Parser:
  def __init__(self, lexer, emitter):
    self.lexer = lexer
    self.emitter = emitter

    self.symbols = set()  # keep track of variables declared.
    self.labels_declared = set()  # labels declared so far.
    self.labels_gotoed = set()  # labels goto'ed so far

    self.current_token = None
    self.peek_token = None

    self.next_token()
    self.next_token()  # Called twice to initialize the current and peek

  # Return true if the current token matches.
  def check_token(self, kind):
    return kind == self.current_token.kind

  # Return true if the next token matches
  def check_peek(self, kind):
    return kind == self.peek_token.kind

  # Try to match the current token. If not, error out. Advance current token
  def match(self, kind):
    if not self.check_token(kind):
      self.abort("Expected " + kind.name + ", got " +
                 self.current_token.kind.name)
    self.next_token()

  # Advances the current token.
  def next_token(self):
    self.current_token = self.peek_token
    self.peek_token = self.lexer.get_token()
    # The lexer handles EOF

  def abort(self, message):
    sys.exit("Error: " + message)

  # Production rules
  # program ::= { statement }
  def program(self):
    # print("PROGRAM")
    self.emitter.header_line("#include <stdio.h>")
    self.emitter.header_line("int main(void){")

    # handle newlines at the start of a file.
    # skip the excess newlines at the start of the file.
    while self.check_token(TokenType.NEWLINE):
      self.next_token()

    # parse all the statements in the program.
    while not self.check_token(TokenType.EOF):
      self.statement()

    # wrap things up
    self.emitter.emit_line("return 0;")
    self.emitter.emit_line("}")

    # make sure that the compiler is not 'GOTOing' to an undeclared label
    for label in self.labels_gotoed:
      if label not in self.labels_declared:
        self.abort("Attempting to GOTO to undeclared label: " + label)

  # One of the following statements
  def statement(self):
    # Check the first token to see what kind of statement this is.

    # "PRINT" (expression | string)
    if self.check_token(TokenType.PRINT):
      # print("STATEMENT-PRINT")
      self.next_token()

      if self.check_token(TokenType.STRING):
        # A simple string
        self.emitter.emit_line("printf(\"" + self.current_token.text +
                               "\\n\");")
        self.next_token()
      else:
        # Expects an expression and print the result as a float
        self.emitter.emit("printf(\"%" + ".2f\\n\", (float)(")
        self.expression()
        self.emitter.emit_line("));")

    # "IF" comparison "THEN" { statement } "ENDIF"
    elif self.check_token(TokenType.IF):
      # print("STATEMENT-IF")
      self.next_token()
      self.emitter.emit("if(")
      self.comparison()

      self.match(TokenType.THEN)
      self.nl()
      self.emitter.emit_line("){")

      # Zero or more statements in the body.
      while not self.check_token(TokenType.ENDIF):
        self.statement()
      self.match(TokenType.ENDIF)

      self.emitter.emit_line("}")

    # "WHILE" comparison "REPEAT" nl { statment nl } "ENDWHILE" nl
    elif self.check_token(TokenType.WHILE):
      # print("STATEMENT-WHILE")
      self.next_token()
      self.emitter.emit("while(")
      self.comparison()
      self.match(TokenType.REPEAT)
      self.nl()
      self.emitter.emit_line("){")

      # Zero or more statements in the loop body.
      while not self.check_token(TokenType.ENDWHILE):
        self.statement()
      self.match(TokenType.ENDWHILE)
      self.emitter.emit_line("}")

    # "LABEL" ident
    elif self.check_token(TokenType.LABEL):
      # print("STATEMENT-LABEL")
      self.next_token()

      # make sure label does as not already been used
      if self.current_token.text in self.labels_declared:
        self.abort("Label already been used: " + self.current_token.text)
      self.labels_declared.add(self.current_token.text)

      self.emitter.emit_line(self.current_token.text + ":")
      self.match(TokenType.IDENT)

    # "GOTO" ident
    elif self.check_token(TokenType.GOTO):
      # print("STATEMENT-GOTO")
      self.next_token()

      # track all the goto'ed labels
      self.labels_gotoed.add(self.current_token.text)
      self.emitter.emit_line("goto " + self.current_token.text + ";")
      self.match(TokenType.IDENT)

    # "LET" ident "=" expression
    elif self.check_token(TokenType.LET):
      # print("STATEMENT-LET")
      self.next_token()

      # check if ident (variables) do not exists in the symbol table. if not declare it
      if self.current_token.text not in self.symbols:
        self.symbols.add(self.current_token.text)
        self.emitter.header_line("float " + self.current_token.text + ";")

      self.emitter.emit(self.current_token.text + " = ")
      self.match(TokenType.IDENT)
      self.match(TokenType.EQ)
      self.expression()
      self.emitter.emit_line(";")

    # "INPUT" ident
    elif self.check_token(TokenType.INPUT):
      # print("STATEMENT-INPUT")
      self.next_token()

      # check if ident (variables) do not exists in the symbol table. if not declare it
      if self.current_token.text not in self.symbols:
        self.symbols.add(self.current_token.text)
        self.emitter.header_line("float " + self.current_token.text + ";")

      # emit scanf but also validate the input. if invalid, set the variable to 0 and clear the input
      self.emitter.emit_line("if(0 == scanf(\"%" + "f\", &" +
                             self.current_token.text + ")) {")
      self.emitter.emit_line(self.current_token.text + " = 0;")
      self.emitter.emit("scanf(\"%")
      self.emitter.emit_line("*s\");")
      self.emitter.emit_line("}")
      self.match(TokenType.IDENT)

    # This is not a valid statement. Error!
    else:
      self.abort("Invalid statement at " + self.current_token.text + " (" +
                 self.current_token.kind.name + ") ")

    # Newline
    self.nl()

  # nl ::= '\n'+
  def nl(self):
    # print("NEWLINE")

    # Require at least one newline.
    self.match(TokenType.NEWLINE)
    # Allow space for extra newlines too just in case
    while self.check_token(TokenType.NEWLINE):
      self.next_token()

  # returns true if the current token is a comparison operator.
  def is_comparison_operator(self):
    return self.check_token(TokenType.GT) or self.check_token(
        TokenType.GTEQ) or self.check_token(TokenType.LT) or self.check_token(
            TokenType.LTEQ) or self.check_token(
                TokenType.EQ) or self.check_token(TokenType.EQEQ)

  # primary ::= number | identifier
  # primary parses our variable.
  def primary(self):
    # print("PRIMARY (" + self.current_token.text + ") ")

    if self.check_token(TokenType.NUMBER):
      self.emitter.emit(self.current_token.text)
      self.next_token()
    elif self.check_token(TokenType.IDENT):
      # ensure the variable exists before they can be used
      if self.current_token.text not in self.symbols:
        self.abort("Referencing variables before assignment: " +
                   self.current_token.text)
      self.emitter.emit(self.current_token.text)
      self.next_token()
    else:
      # Error, unrecognizable token
      self.abort("Unexpected token at " + self.current_token.text)

  # unary ::= ["+" | "-"] primary
  def unary(self):
    # print("UNARY")

    # optional unary +/-
    if self.check_token(TokenType.PLUS) or self.check_token(TokenType.MINUS):
      self.emitter.emit(self.current_token.text)
      self.next_token()
    self.primary()

  # term ::= unary {("/" | "*") unary}
  def term(self):
    # print("TERM")
    self.unary()

    # can have 0 or more `*`or`/` and expressions
    while self.check_token(TokenType.ASTERISK) or self.check_token(
        TokenType.SLASH):
      self.emitter.emit(self.current_token.text)
      self.next_token()
      self.unary()

  # expression ::= term {("-" | "+") term}
  def expression(self):
    # print("EXPRESSION")
    self.term()

    # can have 0 or mare +/- and expressions.
    while self.check_token(TokenType.PLUS) or self.check_token(
        TokenType.MINUS):
      self.emitter.emit(self.current_token.text)
      self.next_token()
      self.term()

  # comparison ::= expression (("==" | "!=" | ">" | ">=" | "<" | "<=") expression)+\
  # only allow comparison between boolean expressions
  def comparison(self):
    # print("COMPARISON")
    self.expression()

    # there must be at least one comparison operator and another expression
    if self.is_comparison_operator():
      self.emitter.emit(self.current_token.text)
      self.next_token()
      self.expression()
    # else:
    # self.abort("Expected comparison operator at: " + self.current_token.text)

    # can have 0 or more comparison operator
    while self.is_comparison_operator():
      self.emitter.emit(self.current_token.text)
      self.next_token()
      self.expression()
