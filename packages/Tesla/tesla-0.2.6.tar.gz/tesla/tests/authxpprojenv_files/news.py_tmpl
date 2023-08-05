from datetime import datetime
from elixir import *
from permissions import has_permissions

class NewsItem(Entity):
    has_field('title', Unicode(100))
    has_field('content', Unicode)
    has_field('published', DateTime, default=datetime.now)
    belongs_to('author', of_kind='authxpprojectname.model.User')
    has_permissions(['edit', 'delete'], precheck='is_author')
    
    def is_author(self, principal, perm):
        return (self.author==principal)
