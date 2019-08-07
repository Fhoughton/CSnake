import os
from pycparser import c_parser

variables = {}
globalpushregister = 8

def getSize(datatype):
    if datatype == 'int':
        return 4
    else:
        return 8
    
def evalConstant(expr, inline):
    inline += "	movl	${}, %eax\n".format(expr.value)
    return inline

def evalID(expr, inline):
    inline += "	movl	{}, %eax\n".format(variables[expr.name])
    return inline

def compExpr():
    pass

def evalExpr(expr, inline):
    if str(expr).startswith("Constant("):
        return evalConstant(expr, inline)
    if str(expr).startswith("BinaryOp("):
        return evalBinaryOp(expr, inline)
    if str(expr).startswith("ID("):
        return evalID(expr, inline)
    else:
        print("OOPS")
    
def evalBinaryOp(expr, inline):
    #FIND A WAY TO CREATE AND RETURN CONSTANTS?
    #ADD MATHS TO OUTPUT HERE
    inline+="	movl	{}, %edx\n".format(evalExpr(expr.left, inline).replace("\n","")) #CREATES THE NEWLINE THING
    inline+="	movl	{}, %eax\n".format(evalExpr(expr.right, inline).replace("\n",""))
    inline+="	addl	%edx, %eax\n"
    inline+="	popl	%ebp\n"
    return inline

source_file = "dummy.c" #input()
assembly_file = os.path.splitext(source_file)[0] + ".s"

with open(source_file, 'r') as infile:
    source = infile.read().strip()

output = ""

parser = c_parser.CParser()
ast = parser.parse(source)
#ast.show() #prints output
#
#show_func_defs(ast)
#show_constants(ast)

#ast.ext[0].show() #returns foo function since first in AST
#ast.ext[1].show() #returns main function since second in AST

#.ext[0] has params ['attr_names', 'body', 'coord', 'decl', 'param_decls']
#ast.ext[0].body.show() returns core of function has ['attr_names', 'block_items', 'coord']
#ast.ext[0].body.block_items[0] returns the return expression, has attributes ['attr_names', 'coord', 'expr']
#ast.ext[0].decl.type.args.params[0].type.type.names returns type info

#example = ast.ext[0].decl.type.args.params[0].type.declname
#members = [attr for attr in dir(example) if not callable(getattr(example, attr)) and not attr.startswith("__")]
#print(example)

#print(ast.ext[0].body.block_items[0].expr)

#Parse the AST, actual compiler work done here
for ext in ast.ext:
    #Log the parameters
    if hasattr(ext.decl.type.args,'params'):
        for param in ext.decl.type.args.params:
            variables[param.type.declname] = str(globalpushregister)+"(%ebp)"
            globalpushregister+=getSize(param.type.type.names)
        
    if ext.decl.name=='main':
        output+="	.globl _main\n"
        
    output+="_{}:\n".format(ext.decl.name)
    
    for item in ext.body.block_items:
        #Handle returning
        if str(item).startswith("Return("):
            # ID(name='x') with foo
            output = evalExpr(item.expr, output)
            output += "	ret\n"
            
with open(assembly_file, 'w') as outfile:
    outfile.write(output)
    
print("globalpushregister",globalpushregister)