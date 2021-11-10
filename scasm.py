import ast


class AssignWrapper(ast.NodeTransformer):
    operations = []
    variables = {}

    def visit_Assign(self, node):
        if isinstance(node.value, ast.Constant):
            for target in node.targets:
                self.variables[target.id] = node.value.value
        elif isinstance(node.value, ast.BinOp):
            self.visit(node.value)
            for target in node.targets:
                self.operations += ["STORE " + target.id]
        # self.generic_visit(node)

    def visit_BinOp(self, node):
        print('Node type: BinOp and fields: ', node._fields)
        print(ast.dump(node))
        self.operations += ["LOAD " + str(node.left.id), "ADD "+ str(node.right.id)]
        self.generic_visit(node)

with open('add_values.sca', 'r') as file:
    tree = ast.parse(file.read())
# print(ast.dump(tree))

wrapper = AssignWrapper()
tree = wrapper.visit(tree)
print(ast.dump(tree))

result = ""

for operation in wrapper.operations:
    result += operation + "\n"

for variable, value in wrapper.variables.items():
    result += variable + ":   DW " + str(value) + "\n"

print(result)
print(wrapper.operations)
print(wrapper.variables)