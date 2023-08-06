"""
    vellum parser
    ~~~~~~~~~~~~~

    this is a simple re.Scanner based recursive parser

    :license: GNU GPL 2 or later
    :copyright: 2009 by Ronny Pfannschmidt

    current issues
    --------------

    * assertion handling of parse errors
    * unbalanced expressions cause StopIteration to pass thru
    * the input parser ignores unbalanced expressions in file sections
"""

import re

# helper types

class ODict(dict):
    """dummy type for saving the order of dictmaker items 
    for later usage in ui's"""
    def __init__(self):
        dict.__init__(self)
        self.order = []

    def add(self, name, expr):
        self[name] = expr
        self.order.append(name)


class ShMarked(str):
    def __new__(cls, data, mark):
        result = str.__new__(cls, data)
        result.flavor = mark
        return result

    #this is convience for tools, strings behave like sh references, so they can be threaded the same
    name = 'sh'

    @property
    def expr(self):
        return self


class Reference(object):
    def __init__(self, name, expr):
        self.name = name
        self.expr = expr
    def __repr__(self):
        return "%s -> %r"%(self.name, self.expr)


# tokenizer

def t(name):
    def _token(scanner, text):
        return name, text, scanner.match.start()
    return _token

scanner = re.Scanner([
    (r'[\r\n\ \t]+', None),
    (r'\#.*\n?', None),
    (r'yes\b', t('true')),
    (r'no\b', t('false')),
    (r'[a-zA-Z][\w.]+', t('name')),
    (r'\b[a-zA-Z]\b', t('shortname')),
    (r'\.[0-9]+|[0-9]+(\.[0-9\.]+)?', t('number')),
    (r"'[^\n']*'", t('string')),
    (r'"[^\n\"]*"', t('string')),
    (r'\(', t('dict_start')),
    (r'\)', t('dict_end')),
    (r'\[', t('list_start')),
    (r'\]', t('list_end')),
    (r'[>$|][^\r\n]+\n', t('shell')),
])

def tokenize(line):
    return scanner.scan(line)[0]


def tokenize_lines(lines):
    for index, line in enumerate(lines):
        for token_type, token, start in tokenize(line):
            yield token_type, token, index+1, start

# parser

def assert_read(iter, *types):
    token_type, token, line, pos = iter.next()
    #XXX: more nice
    assert token_type in types, "%s not in %s, line %s pos %d"%(token_type, types, line, pos)
    return token_type, token, line, pos

def parse_reference(iter):
    token_type, token, line, pos = assert_read(iter, 'name')
    return Reference(token, parse_expr(iter))


def parse_list(iter):
    data = []
    while True:
        next = parse_expr(iter, list)
        if next is None:
            break
        data.append(next)

    return data

def parse_dict(iter):
    data = ODict()
    while True:
        token_type, token, line, pos = assert_read(iter, 'name', 'dict_end')
        if token_type == 'dict_end':
            break
        data.add(token, parse_expr(iter))
    return data



def parse_expr(iter, nesting=None):
    #XXX: ugly
    token_type, token, line, pos = assert_read(iter,
                                               'shortname',
                                               'true', 'false',
                                               'string', 'number',
                                               'shell', 'name',
                                               'list_start',
                                               'list_end',
                                               'dict_start',
                                              )
    if token_type=='shortname':
        #XXX: better errors
        raise SyntaxError("Name '%s' too short - line %d pos %d"%(token, line, pos))
    elif token_type=='true':
        return True
    elif token_type=='false':
        return False
    elif token_type=='number':
        if '.' in token:
            return float(token)
        else:
            return int(token)
    elif token_type=='string':
        return token[1:-1].decode('string_escape')
    elif token_type=='shell':
        return ShMarked(token[1:], token[0]) #XXX: better type
    elif token_type=='name':
        return Reference(token, parse_expr(iter))
    elif token_type=='list_start':
        return parse_list(iter)
    elif token_type == 'dict_start':
        return parse_dict(iter)
    elif token_type == 'list_end':
       assert nesting is list




def parse_input(iter):

    data = ODict()
    while True:
        try:
            token_type, name, line, pos = assert_read(iter, 'name')
            token_type, token, line, pos = assert_read(iter, 'list_start', 'dict_start')
            if token_type=='list_start':
                expr = parse_list(iter)
            else:
                expr = parse_dict(iter)
            data.add(name, expr)
        except StopIteration: 
            # XXX: this ignores unbalanced expressions at the end
            return data

def parse(type, content):
    lines = content.splitlines(True)
    token_stream = tokenize_lines(lines)
    token_list = list(token_stream)
    parser = globals()['parse_'+type]
    return parser(iter(token_list))

