import math
import re


# UTILS FOR READING
def read_nchars(string, n=1):
    """
    Read n characters from string

    @param string str: string you are reading.
    @param n int: number of characters to read.
    """
    return string[:n]


def read_until(string, untilseq=""):
    """
    Read until you find sequence.

    @param string str: string you are reading.
    @param untilseq: sequence to stop when it's next to read.
    """
    idx = string.index(untilseq)
    return string[:idx]


def eat(string, s):
    """
    Eat sequence s from `string`.

    @param string: string you are reading.
    @param s: sequence to eat.
    """
    #SHOULD RAISE HERE.
    return string[len(s):]


def peek(string, n=0):
    """
    Peek into the next `n` characters to be read in string

    @param string: string you are reading.
    @param n: number of characters to peek.
    """
    return string[:n]


# RPN Evaluator (cause i'm too lazy to write extra grammar for expressions).
binop_to_func = {
    "+": lambda x, y: x + y,
    "-": lambda x, y: x - y,
    "*": lambda x, y: x * y,
    "/": lambda x, y: x * 1. / y,
    "^": lambda x, y: x**y,
    "%": lambda x, y: x % y,
    ">": lambda x, y: x > y,
    ">=": lambda x, y: x >= y,
    "<": lambda x, y: x < y,
    "<=": lambda x, y: x <= y,
    "==": lambda x, y: x == y,
    '!=': lambda x, y: x != y,
    'and': lambda x, y: all([x, y]),
    'or': lambda x, y: any([x, y]),
}
# ADD MATH LIBRARY FUNCTIONS HERE BECAUSE IT'S COOL.
mathfuncs = {'!': math.factorial}
for el in dir(math):  # callable objects ( functions ) from math module
    attr = getattr(math, el)
    if callable(attr):
        mathfuncs[el] = attr


def evaluateRPN(expr):
    """
    Evaluate RPN expression.

    @param expr string: rpn expression.
    """
    expr = expr.strip()

    stack = []
    for tok in expr.split(" "):
        if tok in binop_to_func.keys():
            # pop the 2 arguments
            n2 = stack.pop()
            n1 = stack.pop()
            stack.append(binop_to_func[tok](n1, n2))
        elif tok in mathfuncs:
            # pop only 1 argument
            arg = stack.pop()
            stack.append(mathfuncs[tok](arg))
        else:
            stack.append(int(tok))

    if len(stack) == 1:
        return stack[0]


def mineval(expr, ctx):
    """
    RPN eval function to be used in if conditions.

    @param expr str: rpn expression.
    @param ctx  dict: context.
    """
    for k, v in ctx.items():
        if k in expr:
            expr = re.sub(k, str(v), expr)
    return evaluateRPN(expr)

# GRAMMAR
# STMT: VARGET | IFNODE | FORNODE
# IFNODE: %% if EXPR %% STMT+ %% endif %%
# FORNODE: %% for loopvar in looplist %% STMT+ %% endfor %%

class Node:
    """
    Basic AST Class

    @params:
    ctx: dict `environment` for evaluation
    kids: list of asts
    parent: reference to the parent.
    """

    def __init__(self, ctx):
        self._ctx = ctx
        self.kids = []
        self.parent = None

    @property
    def ctx(self):
        if self.parent is not None:
            self._ctx = self.ctx + self.parent.ctx
        return self._ctx

    def node_s(self, lvl=0):
        """
        String representation of the node tree.

        """
        s = ""
        for n in self.kids:
            s += " " * (lvl + 1) + n.node_s(lvl + 1) + "\n\n"
        return s

    def render(self):
        return ''.join(x.render() for x in self.kids)


# Main Root Node of the document contains all the rest
class RootNode(Node):
    """
    Root node for the document `template`
    """
    def render(self):
        return ''.join(x.render() for x in self.kids)


class VarNode(Node):
    """
    Node for accessing variables using %%{{varname}}%% syntax
    """

    def __init__(self, ctx, varname):
        super().__init__(ctx)
        self.varname = varname

    def node_s(self, lvl=0):
        return lvl * " " + """(VarNode: varname:{varname})""".format(varname=self.varname)

    def render(self):
        return str(self.ctx.get(self.varname, None))


class CDataNode(Node):
    """
    Character data node. used to represent textual data.
    """
    def __init__(self, ctx, txt):
        super().__init__(ctx)
        self.txt = txt

    def node_s(self, lvl=0):
        return lvl * " " + "(CDATANode [txt: {txt}])".format(txt=self.txt)

    def render(self):
        return self.txt


class IfNode(Node):
    """
    IfNode: used to represent if conditions

    @attributes
    cond: condition (rpn condition) `simple nothing fancy`
    ifblock: block to be executed if condition is met.
    elseblock: block to be executed if condition isn't met. `to be implemented.`
    """
    def __init__(self, ctx, cond, ifblock, elseblock):
        super().__init__(ctx)
        self.cond = cond
        self.ifblock = ifblock
        self.elseblock = elseblock
        n = parse_template(ifblock, ctx)
        n.parent = self
        self.kids.append(n)

    def render(self):
        if mineval(self.cond, self.ctx):
            return ''.join(x.render() for x in self.kids)
        else:
            return ''

    def node_s(self, lvl=0):
        return lvl * " " + """(IfNode [cond: {cond} ifblock: {ifblock} elseblock:{elseblock} ])""".format(cond=self.cond, ifblock=self.ifblock, elseblock=self.elseblock)


class ForNode(Node):
    """
    ForNode: node representing loops
    %% for loopvar in looplist %%
        loopblock
    %% endfor %%

    """
    def __init__(self, ctx, loopvar, looplist, codeblock):
        super().__init__(ctx)
        self.loopvar = loopvar
        self.looplist = looplist
        self.codeblock = codeblock
        n = parse_template(codeblock, ctx)
        n.parent = self
        self.kids.append(n)

    def node_s(self, lvl=0):
        return lvl * " " + """(ForNode [loopvar: {loopvar} looplist: {looplist} codeblock:{codeblock} ])""".format(loopvar=self.loopvar, looplist=self.looplist, codeblock=self.codeblock)

    def render(self):
        s = ""
        for loopidx, i in enumerate(self.ctx.get(self.looplist)):
            self.ctx['loopidx'] = loopidx
            self.ctx[self.loopvar] = i
            for k in self.kids:
                s += k.render()
        return s


def parse_varnode(template, ctx):
    """
    parse varnode

    @param template str: template.
    @param ctx dict: execution environment.
    """
    template = eat(template, "%% {{")
    varname = read_until(template, "}} %%")
    node = VarNode(ctx, varname)
    template = eat(template, varname)
    template = eat(template, "}} %%")
    return template, node


def parse_ifnode(template, ctx):
    """
    parse IfNode

    @param template str: template
    @param ctx dict: execution environment.
    """
    template = eat(template, "%% if ")
    cond = read_until(template, "%%")
    template = eat(template, cond)
    template = eat(template, " %%")
    ifblock = read_until(template, "%% endif %%")
    template = eat(template, ifblock)
    template = eat(template, "%% endif %%")
    node = IfNode(ctx, cond=cond, ifblock=ifblock, elseblock='')
    return template, node


def parse_fornode(template, ctx):
    """
    parse ForNode

    @param template str: template.
    @param ctx dict: execution environment.
    """
    template = eat(template, "%% for ")
    varname = read_until(template, " in ")
    template = eat(template, varname)
    template = eat(template, " in ")
    looplist = read_until(template, " %%")
    template = eat(template, looplist)
    template = eat(template, " %%")
    loopblock = read_until(template, "%% endfor %%")
    template = eat(template, loopblock)
    template = eat(template, "%% endfor %%")

    node = ForNode(ctx, loopvar=varname,
                   looplist=looplist, codeblock=loopblock)
    return template, node

# STARTERS are %% (if|for|{{)
def parse_template(template, ctx):
    """
    Main parser function.

    @param template str: template to parse.
    @param ctx dict: execution environment.
    """
    root = RootNode(ctx)
    while "%%" in template:
        txt = read_until(template, "%%")
        CDATA = CDataNode(txt=txt, ctx=ctx)
        template = eat(template, txt)
        root.kids.append(CDATA)
        whatisnext = peek(template, 4)
        if whatisnext == "%% {":
            template, node = parse_varnode(template, ctx)
            root.kids.append(node)
        elif whatisnext == "%% i":  # if
            template, node = parse_ifnode(template, ctx)
            root.kids.append(node)
        elif whatisnext == "%% f":  # for
            template, node = parse_fornode(template, ctx)
            root.kids.append(node)
        else:
            pass

    if len(template):
        txt = template
        CDATA = CDataNode(txt=txt, ctx=ctx)
        root.kids.append(CDATA)
    return root


def test1():
    tmpl = """hello %% {{name}} %%"""
    root = parse_template(tmpl, {'name': 'ahmed'})
    print(root.render())


def test2():
    tmpl = """ hello %% {{firstname}} %% %% {{lastname}} %% whatss up?"""
    root = parse_template(tmpl, {'firstname': 'ahmed', 'lastname': 'striky'})
    print(root.render())


def test3():
    tmpl = """
    hello %% {{name}} %%
    %% if 3 5 < %%
    <h1>3 is less than 5</h1>
    %% endif %%
    """
    root = parse_template(tmpl, {'name': 'ahmed', 'x': 99})
    print(root.render())


def test4():
    tmpl = """
    hello %% {{name}} %%
    %% for lang in langs %%
    <h1>%% {{lang}} %%</h1>
    %% endfor %%
    """
    root = parse_template(
        tmpl, {'name': 'ahmed', 'langs': ['py', 'ruby', 'java']})
    print(root.render())

def test5():
    tmpl = """
    hello %% {{name}} %%
    %% for lang in langs %%
    <h1> %% {{lang}} %% </h1>
    %% endfor %%
    %% for num in nums_list %%
    %% if 4 5 == %%
        <h1> has 5 in</h1>
    %% endif %%
    <h1>%% {{num}} %%</h1>
    %% endfor %%
    """
    root = parse_template(tmpl, {'name': 'ahmed', 'langs': [
                          'py', 'ruby', 'java'], 'nums_list': [241, 24, 11]})
    print(root.render())


def test6():
    tmpl = """
    hello %% {{name}} %%
    %% for x in xs %%
    %% if x 5 < %%
    <h1> %% {{x}} %% is less than 5</h1>
    %% endif %%
    %% endfor %%
    """
    root = parse_template(tmpl, {'name': 'ahmed', 'x': 99, 'xs': [3, 2, 1]})
    print(root.render())
if __name__ == "__main__":
    test1()
    test2()
    test3()
    test4()
    test5()
    test6()
