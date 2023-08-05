from projectname.tests import *

class TestNews(TestModel):
    def test_execute(self):
        assert model.execute('select * from newsitems')
    def test_create(self):
        newsitem = model.NewsItem(title = 'foo', content = 'bar')
        newsitem.flush()
        self.failUnlessEqual(2, model.NewsItem.count())