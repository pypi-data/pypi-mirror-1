from projectname.tests import *
from projectname.lib import fixtures

import os

class TestNews(TestModel):
    __fixtures__ = {"news":model.NewsItem}
    def test_fixtures_loaded(self):
        assert self.fixtures['news']["first"]
        assert model.NewsItem.get_by(title="This is the headline")
    def test_execute(self):
        assert model.execute('select * from newsitems')
    def test_dump_data_to_fixtures(self):
        fixtures.dump_data(model.NewsItem)
        fixture_file = os.path.join(os.getcwd(), 'projectname', 'fixtures', 'news', 'newsitems.json')
        assert os.path.exists(fixture_file)
        