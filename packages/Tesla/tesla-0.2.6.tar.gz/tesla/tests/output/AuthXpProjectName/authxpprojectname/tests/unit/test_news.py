from authxpprojectname.tests import *

class TestNews(TestModel):
    def setUp(self):
        TestModel.setUp(self)
        self.user = model.User(username = 'admin', password = 'admin1', email = 'admin@localhost')
        self.user2 = model.User(username = 'tester', password = 'test1', email = 'tester@localhost')
        self.user2.flush()
        self.newsitem = model.NewsItem(title='test', content='testing', author=self.user)
        model.flush_all()
    def test_author_permissions(self):
        assert self.user.has_permission('edit', self.newsitem)
        assert self.user.has_permission('delete', self.newsitem)
    def test_grant_permissions(self):
        assert not self.user2.has_permission('edit', self.newsitem)
        assert not self.user2.has_permission('delete', self.newsitem)
        self.newsitem.grant_permissions_for_user(self.user2)
        assert self.user2.has_permission('edit', self.newsitem)
        assert self.user2.has_permission('delete', self.newsitem)
        self.newsitem.revoke_permissions_for_user(self.user2, 'delete')
        assert self.user2.has_permission('edit', self.newsitem)
        assert not self.user2.has_permission('delete', self.newsitem)

