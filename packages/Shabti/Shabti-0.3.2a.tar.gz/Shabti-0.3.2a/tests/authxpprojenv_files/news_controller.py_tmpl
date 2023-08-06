from authxpprojectname.lib.base import *

class NewsController(BaseController):
    __model__ = model.NewsItem
    def index(self):
        c.newsitems = model.NewsItem.select()
        return len(c.newsitems)
    def view(self, id):
        return 'viewing news item %s' % c.newsitem.title 
    @authorize(permissions.HasPermission('edit', 'newsitem'))
    def edit(self, id):
        return 'editing news item %s' % c.newsitem.title
    