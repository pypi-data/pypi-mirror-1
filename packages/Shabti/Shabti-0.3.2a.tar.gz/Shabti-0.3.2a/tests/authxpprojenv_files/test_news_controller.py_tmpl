from authxpprojectname.tests import *
from paste.fixture import AppError

class TestNews(TestController):
    def setUp(self):
        TestController.setUp(self)
        self.user = model.User(username = 'admin', password = 'admin1', email = 'admin@localhost')
        self.newsitem = model.NewsItem(title='test', content='testing', author=self.user)
        model.flush_all()
    def test_edit_news(self):
        self.login_user('admin', 'admin1')
        resp = self.app.get(url_for(controller='news', action = 'edit', id=self.newsitem.id))
        assert resp.status == 200
       
