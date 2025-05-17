from html.parser import HTMLParser

class Element:
    def __init__(self, name, attrs=None, parent=None):
        self.name = name
        self.attrs = dict(attrs or [])
        self.children = []
        self.parent = parent
        self.text = ""

    def append(self, element):
        self.children.append(element)
        element.parent = self

    def _iter(self):
        yield self
        for child in self.children:
            yield from child._iter()

    def find(self, name=None, attrs=None):
        for el in self._iter():
            if el is self:
                continue
            if name is None or el.name == name or (isinstance(name, (list, tuple)) and el.name in name):
                if attrs is None or all(el.attrs.get(k) == v or (v is True and k in el.attrs) for k, v in attrs.items()):
                    return el
        return None

    def find_all(self, name=None, attrs=None):
        results = []
        for el in self._iter():
            if el is self:
                continue
            if name is None or el.name == name or (isinstance(name, (list, tuple)) and el.name in name):
                if attrs is None or all(el.attrs.get(k) == v or (v is True and k in el.attrs) for k, v in attrs.items()):
                    results.append(el)
        return results

    def has_attr(self, key):
        return key in self.attrs

    def get(self, key, default=None):
        return self.attrs.get(key, default)

    def __getitem__(self, key):
        return self.attrs[key]

class _Parser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.root = Element('[document]')
        self.current = self.root

    def handle_starttag(self, tag, attrs):
        el = Element(tag, attrs, parent=self.current)
        self.current.append(el)
        self.current = el

    def handle_endtag(self, tag):
        while self.current is not None and self.current.name != tag:
            self.current = self.current.parent
        if self.current is not None:
            self.current = self.current.parent or self.root

    def handle_data(self, data):
        if self.current:
            self.current.text += data

class BeautifulSoup(Element):
    def __init__(self, markup, parser='html.parser'):
        parser = _Parser()
        parser.feed(markup)
        super().__init__('[document]')
        self.children = parser.root.children
        for child in self.children:
            child.parent = self

    @property
    def title(self):
        return self.find('title')

