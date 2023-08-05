from xml.dom import minidom

def ws_chop(s):
    c = 0
    while s[0] == ' ':
        c += 1
        s = s[1:]
    return (c, s)

from re import compile as regex_compile, IGNORECASE

tagdefn = regex_compile(r'(\w+)(.*?):\s*(;.*)*$', IGNORECASE)
whitespace = regex_compile(r'\s+')
assignment = regex_compile(r'(?<!\\)=')

def parse_attributes(s):
    in_quote = False
    this = ''
    last = None
    bits = list()

    for c in s:
        if c == '"':
            in_quote = not in_quote
            this += c
        elif not in_quote and c == ' ':
            yield this
            this = ''
        else:
            this +=c
        last = c

    if not in_quote and 0 < len(this):
        yield this

class Tag(object):
    __slots__ = ('name', 'attrs', 'children', 'parent')

    def __init__(self, name, attrs=None, children=None):
        self.name = name
        if attrs is None:
            attrs = dict()
        self.attrs = attrs
        if children is None:
            children = list()
        self.children = children
        self.parent = None

    def __eq__(self, other):
        return (other.name == self.name
                    and other.attrs == self.attrs)

    def __ne__(self, other):
        return not self == other

    def add_child(self, other):
        self.children.append(other)
        other.parent = self

    def __repr__(self):
        return '<Tag %r %r>' % (self.name, self.attrs)

    def __str__(self):
        mytag = '<' + self.name
        attrs = ' '.join('='.join(t) for t in self.attrs.iteritems())
        if 0 < len(attrs):
            mytag += ' ' + attrs

        if 0 == len(self.children):
            return mytag + '/>'
        return mytag + '>' + ''.join(map(str, self.children)) + '</' + self.name + '>'

class Text(str):
    pass

class SurelyParser(object):
    """
    This class is responsible for constructing Tag objects
    from the line-iterable it is passed.  It doesn't know
    anything about HTML.
    """
    def __init__(self, file_like):
        self.file_like = file_like
        self._current_indent = 0
        self._indent_increment = None
        self._tags = dict()
        self._text_buffer = list()

        self._last_parent = None
        self._last_sibling = None

    def _parse_tag_defn(self, line, indent, is_child):
        match = tagdefn.match(line)
        try:
            (tag_name, attrs, inline_text) = match.groups()
        except AttributeError:
            raise ValueError('malformed tag definition: %r' % (line,))
        attr_map = dict()
        attrs = attrs.strip()

        if 0 < len(attrs):
            for assn in parse_attributes(attrs):
                try:
                    (k, v) = assignment.split(assn, 1)
                except ValueError:
                    raise ValueError('unable to parse assignment %r from %r' % (assn, line))
                if v[0] != '"':
                    v = '"' + v + '"'
                attr_map[k] = v

        tag = Tag(tag_name, attr_map)
        self._add(tag, indent, is_child)

        if inline_text is not None:
            self._parse_text(inline_text, indent+1, True)

    def _add(self, thing, indent, is_child):
        if indent not in self._tags:
            self._tags[indent] = list()

        if is_child:
            self._tags[indent-1][-1].add_child(thing)
        elif 0 < indent:
            self._tags[indent][-1].parent.add_child(thing)

        self._tags[indent].append(thing)

    def _parse_text(self, text, indent, is_child):
        self._add(Text(text[1:]), indent, is_child)

    def parse(self):
        for (i, line) in enumerate(self.file_like):

            if line.isspace():
                continue
            if line.startswith('\t'):
                raise ValueError('no tabs, sorry, line %s' % (i,))

            (indent, line) = ws_chop(line)

            if self._indent_increment is None:
                if 0 < indent:
                    self._indent_increment = indent
                else:
                    level = 0

            if self._indent_increment is not None:
                (level, diff) = divmod(indent, self._indent_increment)
                if 0 < diff:
                    raise ValueError('inconsistent indentation')

            is_child = self._current_indent < indent
            self._current_indent = indent

            if line.startswith(';'):
                self._parse_text(line, level, is_child)
            else:
                self._parse_tag_defn(line, level, is_child)

        return self._tags[0][0]
