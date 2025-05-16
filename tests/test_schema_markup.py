import importlib
import sys
import types
import unittest

# Create dummy dependencies for modules
class Dummy:
    def __call__(self, *args, **kwargs):
        return self
    def __getattr__(self, name):
        return self
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc, tb):
        pass

dummy_streamlit = Dummy()
sys.modules.setdefault('streamlit', dummy_streamlit)
sys.modules.setdefault('requests', types.ModuleType('requests'))
bs4_module = types.ModuleType('bs4')
bs4_module.BeautifulSoup = lambda *args, **kwargs: None
sys.modules.setdefault('bs4', bs4_module)
sys.modules.setdefault('pandas', types.ModuleType('pandas'))

ai_checker = importlib.import_module('ai_readiness_checker')
analyze = importlib.import_module('analyze_website')
app = importlib.import_module('app')

class DummyTag:
    def __init__(self, text=None, attrs=None):
        self.text = text
        self.attrs = attrs or {}
    def get(self, key, default=None):
        return self.attrs.get(key, default)

class DummySoup:
    def __init__(self, scripts=None, micro=None):
        self._scripts = scripts or []
        self._micro = micro or []
    def find_all(self, name=None, type=None, attrs=None):
        if name == "script" and type == "application/ld+json":
            return self._scripts
        if attrs == {"itemscope": True}:
            return self._micro
        return []

class SchemaMarkupTests(unittest.TestCase):
    def test_ai_checker_jsonld_mixed_case(self):
        soup = DummySoup([DummyTag('{"@context": "https://Schema.org"}')])
        found, _ = ai_checker.check_schema_markup(soup)
        self.assertTrue(found)

    def test_analyze_website_jsonld_mixed_case(self):
        soup = DummySoup([DummyTag('{"@context": "HTTP://SCHEMA.ORG"}')])
        found, _ = analyze.check_schema_markup(soup)
        self.assertTrue(found)

    def test_app_jsonld_and_microdata(self):
        soup = DummySoup(
            [DummyTag('{"@context": "https://schema.ORg"}')],
            [DummyTag(attrs={'itemtype': 'https://schema.org/Article'})]
        )
        found, details = app.check_schema_markup(soup)
        self.assertTrue(found)
        self.assertIn("JSON-LD", details)
        self.assertIn("Microdata", details)

if __name__ == '__main__':
    unittest.main()
