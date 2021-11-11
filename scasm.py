import ast
from inspect import currentframe
from io import UnsupportedOperation
from typing import Any


class AssignWrapper(ast.NodeTransformer):
    current_while = 0

    labels = set()
    operations = []
    variables = {}

    def maybe_newline(self):
        """Adds a newline if it isn't the start of generated source"""
        if self._source:
            self.write("\n")

    def myvisit(self, node):
        """Outputs a source code string that, if converted back to an ast
        (using ast.parse) will generate an AST equivalent to *node*
        This is the starting point"""
        self._source = []
        self.traverse(node)
        return "".join(self._source)

    def write(self, text):
        """Append a piece of text"""
        self._source.append(text)

    def traverse(self, node):
        """Recursively iterate through an AST"""
        if isinstance(node, list):
            for item in node:
                self.traverse(item)
        else:
            super().visit(node)
        
    def _write_constant(self, value):
        if isinstance(value, (float, complex)):
            raise UnsupportedOperation("floats and complex numbers not supported")
        else:
            self.write(repr(value))

    def visit_Constant(self, node: ast.Constant) -> Any:
        value = node.value
        if isinstance(value, tuple):
            raise UnsupportedOperation("Tuples not supported")
        elif value is ...:
            raise UnsupportedOperation("Ellipses not supported")
        else:
            if node.kind == "u":
                raise UnsupportedOperation("u strings not supported")
            self._write_constant(node.value)

    def visit_Assign(self, node: ast.Assign):
        self.maybe_newline()
        if len(node.targets) > 1:
            raise UnsupportedOperation("Multi-assign not supported")
        
        self.write(f'{node.targets[0].id}:     DW ')

        self.traverse(node.value)

    def visit_While(self, node: ast.While):
        self.maybe_newline()
        this_while = self.current_while # Store current while to jump back to it later
        self.current_while += 1

        self.write(f'while_{this_while}:')
        self.traverse(node.body) # Place body inside while loop
        self.write("\n") # Place newline before JUMP
        self.write(f'JUMP while_{this_while}')

    # def visit_BinOp(self, node):
    #     print('Node type: BinOp and fields: ', node._fields)
    #     print(ast.dump(node))
    #     self.operations += ["LOAD " + str(node.left.id), "ADD "+ str(node.right.id)]
    #     self.generic_visit(node)

with open('add_values.sca', 'r') as file:
    tree = ast.parse(file.read())
# print(ast.dump(tree))

wrapper = AssignWrapper()
print(ast.dump(tree))
tree = wrapper.myvisit(tree)

result = ''.join(wrapper._source)

print(result)

with open('result.acm', 'w') as file:
    file.writelines(result)

# import subprocess
# return_code = subprocess.call(['python', 'pyscasm/scasm.py', '-o', 'drive', '-a', 'result.acm'])

# if return_code != 0:
#     print("Process did not complete cleanly, return code : ", return_code)
