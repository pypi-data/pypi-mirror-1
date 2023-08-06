from authprojectname.tests import *
from paste.fixture import AppError

class TestAuth(TestController):
    def setUp(self):
        TestController.setUp(self)
        self.user = model.User(username = 'admin', password = 'admin1', email = 'admin@localhost')
        admins = model.Group(name = 'Admins')
        permission = model.Permission(name = 'add_users')
        model.flush_all()
        self.user.groups.append(admins)
        admins.permissions.append(permission)
        model.flush_all()
        self.user.refresh()
    def test_signed_in(self):
        self.login_user('admin', 'admin1')
        resp = self.app.get(url_for(controller='auth', action = 'index'))
        assert 'Add user' in resp
        assert 'Post' in resp
        resp = self.app.post(url_for(controller='auth', action = 'add_user'))
        self.failIfEqual(url_for(controller='login'), resp.header_dict.get('location'))
        resp = self.app.get(url_for(controller='auth', action = 'post'))
        self.failIfEqual(url_for(controller='login'), resp.header_dict.get('location'))
    def test_not_signed_in(self):
        resp = self.app.get(url_for(controller='auth', action = 'index'))
        assert 'Add user' not in resp
        assert 'Post' not in resp
        try:
            resp = self.app.get(url_for(controller='auth', action = 'add_user'))
        except AppError, e:
            assert '403' in str(e)
        try:
            resp = self.app.get(url_for(controller='auth', action = 'post'))
        except AppError, e:
            assert '403' in str(e)
       
