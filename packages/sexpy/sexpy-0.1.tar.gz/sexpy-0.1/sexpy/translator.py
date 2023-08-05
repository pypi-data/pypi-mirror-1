# Copyright 2007 Ero-sennin
#
# This file is part of SEXpy.
#
# SEXpy is free software; you can redistribute it and/or modify
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 2 of the License, or (at your
# option) any later version.
#
# SEXpy is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with pybtex; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301
# USA

import sys
import compiler
from compiler import ast
from compiler.consts import OP_ASSIGN, OP_APPLY
from sexpy.parser import String, List

expression_operators = {}
statement_operators = {}

def lineno(obj):
    """Tries to obtain a line number from the code"""

    try:
        return obj.lineno
    except AttributeError:
        return None

def add_lineno(f):
    """A decorator for code generation functions for automatically adding
    a lineno to the resulting Python AST node
    """
    def new_f(code):
        node = f(code)
        node.lineno = lineno(code)
        return node
    return new_f

def expression_operator(op):
    """A decorator function for registering expression operators"""

    def register(f):
        f = add_lineno(f)
        expression_operators[op] = f
        return f
    return register

def statement_operator(op):
    """A decorator function for registering statement operators"""
    def register(f):
        f = add_lineno(f)
        statement_operators[op] = f
        return f
    return register

def make_unary_operator(node):
    """Create a function that will create an AST node for an unary operator"""
    @add_lineno
    def f(args):
        return node(expression(args[1]))
    return f

def make_binary_operator(node):
    """Create a function that will create an AST node for a binary operator"""
    @add_lineno
    def f(args):
        return node(expressions(args[1:]))
    return f

def make_comparison_operator(op):
    """Create a function that will create an AST node for a comparison operator"""
    @add_lineno
    def f(args):
        return ast.Compare(expression(args[1]), [(op, expression(args[2]))])
    return f

expression_operators.update(
    (op, make_binary_operator(node)) for (op, node) in (
        ('+', ast.Add),
        ('-', ast.Sub),
        ('*', ast.Mul),
        ('/', ast.Div),
        ('//', ast.FloorDiv),
        ('**', ast.Power),
        ('%', ast.Mod),
        ('|', ast.Bitor),
        ('&', ast.Bitand),
        ('^', ast.Bitxor),
        ('or', ast.Or),
        ('and', ast.And),
        ))

expression_operators.update(
    (op, make_unary_operator(node)) for (op, node) in (
        ('not', ast.Not),
        ('~', ast.Invert),
        ))

statement_operators.update(
    (op, make_unary_operator(node)) for (op, node) in (
        ('return', ast.Return),
        ))

# yield became an expression in 2.5
if sys.version_info[0] == 2 and sys.version_info[1] >= 5:
    expression_operators['yield'] = make_unary_operator(ast.Yield)
else:
    statement_operators['yield'] = make_unary_operator(ast.Yield)

expression_operators.update(
    (op, make_comparison_operator(op)) for op in (
        ('==', '!=' ,'<', '>', '<=', '>=', 'is')
        ))

@statement_operator('=')
def assign(code):
    assert len(code) == 3
    lvalue = expression(code[1])
    rvalue = expression(code[2])
    l = lineno(code)
    if isinstance(lvalue, ast.Name):
        return ast.Assign([ast.AssName(lvalue.name, OP_ASSIGN)], rvalue)
    elif isinstance(lvalue, ast.Getattr):
        return ast.Assign(
                [ast.AssAttr(lvalue.expr, lvalue.attrname, OP_ASSIGN)],
                rvalue)
    elif isinstance(lvalue, ast.Subscript):
        lvalue.flags = OP_ASSIGN
        return ast.Assign([lvalue], rvalue)
    else:
        raise SyntaxError

@expression_operator('.')
def getattr_(args):
    return ast.Getattr(expression(args[1]), args[2])

@expression_operator('..')
def subscript(args):
    return ast.Subscript(expression(args[1]), OP_APPLY, expressions(args[2:]))

@statement_operator('class')
def class_(code):
    declaration = code[1]
    name = declaration[0]
    bases = expressions(declaration[1:])
    body = statements(code[2:])
    return ast.Class(name, bases, None, body)

@statement_operator('def')
def def_(code):
    signature = code[1]
    name = signature[0]
    args = signature[1:]
    body = statements(code[2:])
    return ast.Function(None, name, args, [], 0, None, body)

@statement_operator('from')
def from_(code):
    assert len(code) >= 3
    if code[2] == 'import':
        names = code[3:]
    else:
        names = code[2:]
    return ast.From(code[1], [(module, None) for module in names], 0)

@statement_operator('for')
def for_(code):
    assert len(code) >= 3
    return ast.For(ast.AssName(code[1], OP_ASSIGN), expression(code[2]), statements(code[3:]), None)

@statement_operator('if')
def if_(code):
    assert len(code) >= 2
    else_clause = None
    clauses = []
    for clause in code[1:]:
        if clause[0] == 'else':
            else_clause = statements(clause[1:])
        else:
            clauses.append((expression(clause[0]), statements(clause[1:])))

    return ast.If(clauses, else_clause)

@statement_operator('import')
def import_(code):
    assert len(code) >= 2
    return ast.Import([(module, None) for module in code[1:]])
        
@statement_operator('print')
def print_(args):
    return ast.Printnl(expressions(args[1:]), None)

@statement_operator('raise')
def raise_(code):
    assert len(code) == 2
    return ast.Raise(expression(code[1]), None, None)

def expressions(code):
    return [expression(e) for e in code]

def expression(code):
    """Create a Python AST node for an arbitrary SEXpy expression"""
    if isinstance(code, (int, long)):
        return ast.Const(code) #, lineno(code))
    elif isinstance(code, String):
        return ast.Const(str(code)) #, lineno=lineno(code))
    elif isinstance(code, List):
        return ast.List(expressions(code))
    elif isinstance(code, basestring):
        return name(code) #, lineno(code))
    else:
        op = code[0]
        try:
            operator = expression_operators[op]
        except (KeyError, TypeError):
            return call(code)
        return operator(code)

def name(s):
    l = s.split('.')
    obj = ast.Name(l[0])
    for attr in l[1:]:
        obj = ast.Getattr(obj, attr)
    return obj

@add_lineno
def statement(code):
    """Create a Python AST node for an arbitrary SEXpy statement (or expression)"""
    try:
        op = code[0]
    except:
        return ast.Discard(expression(code))
    try:
        operator = statement_operators[op]
    except (KeyError, TypeError):
        return ast.Discard(expression(code))
    return operator(code)

def statements(code):
    return ast.Stmt([statement(i) for i in code])

@add_lineno
def call(code):
    return ast.CallFunc(expression(code[0]), expressions(code[1:]), None, None)

def module(code):
    return ast.Module(None, statements(code))

def to_python_ast(sex_ast):
    """Create a Python AST from a SEXpy AST"""
    return module(sex_ast)

def compile(sex_ast, filename='<input>', codegen = compiler.pycodegen.ModuleCodeGenerator):
    """Create a Python code object from a SEXpy AST"""

    python_ast = to_python_ast(sex_ast)
    compiler.misc.set_filename(filename, python_ast)
    return codegen(python_ast).getCode()
