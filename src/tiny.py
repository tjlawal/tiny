from lexer import *
from emitter import *
from parser import *
import sys

def main():
  print("Tiny Basic to C Compiler")

  # NOTE(tijani): sys.argv is zero indexed (0 - script name, 1 - argument), checking for 2 makes sense because there
  # are two elements in the list
  if len(sys.argv) != 2:
    sys.exit("Error: Compiler needs source file as argument.")
  with open(sys.argv[1], 'r') as input_file:
    input = input_file.read()

  lexer = Lexer(input)
  emitter = Emitter(sys.argv[1] + ".c")
  parser = Parser(lexer, emitter)

  parser.program()  # start
  emitter.write_file()  # Write the output to file
  print("Parsing Completed.")

main()
