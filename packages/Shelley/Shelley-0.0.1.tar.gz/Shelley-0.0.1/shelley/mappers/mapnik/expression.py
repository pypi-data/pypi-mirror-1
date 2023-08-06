# Lifted from http://effbot.org/zone/simple-top-down-parsing.htm
import operator
import re


# symbol registry
symbol_table = {}


class symbol_base(object):

    id = None
    value = None
    first = second = third = None

    def nud(self):
        raise SyntaxError("Syntax error (%r)." % self.id)
    
    def led(self, left):
        raise SyntaxError("Unknown operator (%r)." % self.id)

    def __repr__(self):
        if self.id == "(name)" or self.id == "(literal)":
            return "(%s %s)" % (self.id[1:-1], self.value)
        out = [self.id, self.first, self.second, self.third]
        out = map(str, filter(None, out))
        return "(" + " ".join(out) + ")"


def symbol(id, bp=0):
    try:
        s = symbol_table[id]
    except KeyError:
        class s(symbol_base):
            pass
        s.__name__ = "symbol-" + id # for debugging
        s.id = id
        s.value = None
        s.lbp = bp
        symbol_table[id] = s
    else:
        s.lbp = max(bp, s.lbp)
    return s


# helpers

def infix(id, bp):
    def led(self, left):
        self.first = left
        self.second = expression(bp)
        return self
    symbol(id, bp).led = led


def infix_r(id, bp):
    def led(self, left):
        self.first = left
        self.second = expression(bp-1)
        return self
    symbol(id, bp).led = led


def prefix(id, bp):
    def nud(self):
        self.first = expression(bp)
        return self
    symbol(id).nud = nud


def advance(id=None):
    global token
    if id and token.id != id:
        raise SyntaxError("Expected %r" % id)
    token = next()


def method(s):
    # decorator
    assert issubclass(s, symbol_base)
    def bind(fn):
        setattr(s, fn.__name__, fn)
    return bind


# tokenizer

def tokenize(program):
    last_end = 0
    for match in token_pat.finditer(program):
        start = match.start()
        if start != last_end:
            raise SyntaxError("Can't tokenize %r" % program[last_end:start])
        else:
            last_end = match.end()
        groupdict = match.groupdict()
        if groupdict['number'] is not None:
            symbol = symbol_table["(literal)"]
            s = symbol()
            s.value = int(groupdict['number'])
            yield s
        elif groupdict['string'] is not None:
            symbol = symbol_table["(literal)"]
            s = symbol()
            s.value = groupdict['string'][1:-1]
            yield s
        elif groupdict['name'] is not None:
            symbol = symbol_table["(name)"]
            s = symbol()
            s.value = groupdict['name'][1:-1]
            yield s
        else:
            symbol = symbol_table.get(groupdict['operator'])
            if not symbol:
                raise SyntaxError("Unknown operator in %r" % program)
            yield symbol()
    if last_end != len(program):
        raise SyntaxError("Can't tokenize %r" %
                          program[last_end:])
    symbol = symbol_table["(end)"]
    yield symbol()

    
# parser

def expression(rbp=0):
    global token
    t = token
    token = next()
    left = t.nud()
    while rbp < token.lbp:
        t = token
        token = next()
        left = t.led(left)
    return left


def parse(program):
    try:
        global token, next
        next = tokenize(program).next
        token = next()
        e = expression()
        if token.id != '(end)':
            raise SyntaxError('Too many tokens')
        return e
    except StopIteration:
        raise SyntaxError("Input ended early")


# evaluation

def evaluate(expression, context={}):
    return parse(expression).eval(context)


## mapnik expressions

# tokens

token_pat = re.compile("""
                       \s*
                       (
                           (?P<number>\d+)
                           |
                           (?P<string>(?P<quote>"|').*?(?P=quote))
                           |
                           (?P<name>\[[^\]]+?\])
                           |
                           (?P<operator>(\(|\)|and|or|not|<>|<=|>=|<|>|=))
                       )
                       \s*""",
                       re.VERBOSE)


# syntax

infix_r("or", 30)
infix_r("and", 40)
prefix("not", 50)

infix("<", 60)
infix(">", 60)
infix("<=", 60)
infix(">=", 60)
infix_r("<>", 60)
infix_r("=", 60)

symbol("(", 150)

symbol("(name)").nud = lambda self: self
symbol("(literal)").nud = lambda self: self

symbol("(end)")

symbol(")")

@method(symbol("("))
def nud(self):
    expr = expression()
    advance(")")
    return expr


# evaluation

def prefix_eval(id, op):
    def eval(self, ctx):
        return op(self.first.eval(ctx))
    symbol(id).eval = eval


def infix_eval(id, op):
    def eval(self, ctx):
        return op(self.first.eval(ctx), self.second.eval(ctx))
    symbol(id).eval = eval


infix_eval("or", operator.or_)
infix_eval("and", operator.and_)
prefix_eval("not", operator.not_)

infix_eval("<", operator.lt)
infix_eval(">", operator.gt)
infix_eval("<=", operator.le)
infix_eval(">=", operator.ge)
infix_eval("<>", operator.ne)
infix_eval("=", operator.eq)

@method(symbol("(literal)"))
def eval(self, ctx):
    return self.value

@method(symbol("(name)"))
def eval(self, ctx):
    return ctx[self.value]
