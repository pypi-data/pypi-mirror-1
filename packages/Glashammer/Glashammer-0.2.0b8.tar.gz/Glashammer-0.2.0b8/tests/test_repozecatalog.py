

from unittest import TestCase

from repoze.catalog.indexes.field import CatalogFieldIndex
from repoze.catalog.indexes.text import CatalogTextIndex
from repoze.catalog.catalog import ConnectionManager

from glashammer.utils import Response
from glashammer.application import make_app
from glashammer.bundles.repozecatalog import setup_repozecatalog, \
        get_repozecatalog, create_dumb_index, index_document, \
        search_catalog

from werkzeug.test import Client

def get_flavor(object, default):
    return getattr(object, 'flavor', default)

def get_text(object, default):
    return getattr(object, 'description', default)

class IceCream(object):
    color = 'white'
    def __init__(self, flavor, description):
        self.flavor = flavor
        self.description = description


class TestRepozeCatalog(TestCase):

    def setUp(self):
        self.app = make_app(self._setup, 'test_output')
        self.c = Client(self.app)

    def test_event_setup(self):
        assert self.catalog

    def test_setup(self):
        assert 'flavor' in self.catalog
        assert 'text' in self.catalog

    def test_setup_twice(self):
        f1, t1 = self.catalog['flavor'], self.catalog['text']
        app = make_app(self._setup, 'test_output')
        f2, t2 = self.catalog['flavor'], self.catalog['text']
        assert t1 is t2
        assert f1 is f2

    def test_index(self):
        a, r, h = self.c.open()
        assert ''.join(a) == ''

    def test_search(self):
        a, r, h = self.c.open()
        t = self.catalog.search(text='nuts')[0]
        assert t == 1
        t = self.catalog.search(text='ice')[0]
        assert t == 2
        t = self.catalog.search(text='glashammer')[0]
        assert t == 0
        t = self.catalog.search(color='white')[0]
        assert t == 2
        t = search_catalog(color='white')[0]
        assert t == 2


    def _setup(self, app):
        app.add_setup(setup_repozecatalog)
        app.connect_event('repozecatalog-installed', self._on_catalog_installed)
        app.add_url('/', 'test/dummy', self._dummy_view)

    def _on_catalog_installed(self, catalog):
        manager = ConnectionManager()
        if 'flavor' not in self.catalog:
            catalog['flavor'] = CatalogFieldIndex(get_flavor)
        if 'text' not in self.catalog:
            catalog['text'] = CatalogTextIndex(get_text)
        if 'color' not in self.catalog:
            create_dumb_index(CatalogTextIndex, 'color')
        manager.commit()

    def _dummy_view(self, req):
        manager = ConnectionManager()
        peach = IceCream('peach', 'This ice cream has a peachy flavor')
        self.catalog.index_doc(1, peach)
        pistachio = IceCream('pistachio', 'This ice cream tastes like pistachio nuts')
        index_document(2, pistachio)
        manager.commit()
        return Response('')


    @property
    def catalog(self):
        return get_repozecatalog()
