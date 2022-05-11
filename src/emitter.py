## The emitter keeps track of the generated code and outputs it.
class Emitter:
  def __init__(self, full_path):
    self.full_path = full_path
    self.header = ""
    self.code = ""

# add a fragment of C code

  def emit(self, code):
    self.code += code

# add a fragment of C code that ends a line.

  def emit_line(self, code):
    self.code += code + '\n'

# to add a line of C code to the top of the C code file, this includes
#  headers, main and variable declaration

  def header_line(self, code):
    self.header += code + '\n'

# save file
  def write_file(self):
    with open(self.full_path, 'w') as output_file:
      output_file.write(self.header + self.code)
