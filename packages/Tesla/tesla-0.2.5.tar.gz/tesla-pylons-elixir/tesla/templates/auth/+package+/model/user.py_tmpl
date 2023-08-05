from datetime import datetime
from elixir import *

class User(Entity):
    has_field('username', Unicode(30), unique=True, required=True)
    has_field('password', Unicode(50))
    has_field('email', String(255), unique=True, required=True)
    has_field('created', DateTime, default=datetime.utcnow)
    has_field('active', Boolean, default=True)
    has_and_belongs_to_many('groups', of_kind='Group', inverse='members')

    @classmethod
    def authenticate(cls, username, password):
        return cls.get_by(username=username, 
                          password=password, 
                          active=True)

    @property
    def permissions(self):
        permissions = set()
        for g in self.groups:
            permissions = permissions | set(g.permissions)
        return permissions        

    @property
    def permission_names(self):
        return [p.name for p in self.permissions]

    def has_permission(self, perm):
        return (perm in self.permission_names)

class Group(Entity):
    has_field('name', Unicode(30), unique=True, required=True)
    has_field('description', Unicode(255))
    has_field('created', DateTime, default=datetime.utcnow)
    has_field('active', Boolean, default=True)
    has_and_belongs_to_many('members', of_kind='User', inverse='groups')
    has_and_belongs_to_many('permissions', of_kind='Permission', inverse='groups')

class Permission(Entity):
    has_field('name', Unicode(16), unique=True, required=True)
    has_field('description', Unicode(255))
    has_and_belongs_to_many('groups', of_kind='Group', inverse='permissions')

