from datetime import datetime
from elixir import *
from elixir import events
import hashlib

class NotAuthenticated(Exception):pass

def encrypt_value(value):
    return hashlib.sha1(value).hexdigest()

class User(Entity):
    has_field('username', Unicode(30), unique=True, required=True)
    has_field('password', String(40))
    has_field('password_check', String(40))
    has_field('email', String(255), unique=True, required=True)
    has_field('created', DateTime, default=datetime.utcnow)
    has_field('active', Boolean, default=True)
    has_and_belongs_to_many('groups', of_kind='Group', inverse='members')
    
    @classmethod
    def authenticate(cls, username, password):
        user=cls.get_by(username=username, active=True)
        if user and encrypt_value(password) == user.password:
            return user
        raise NotAuthenticated

    @events.before_insert
    @events.before_update
    def encrypt_password(self):
        if self.password and self.password != self.password_check:
            self.password = encrypt_value(self.password)
            self.password_check = self.password

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

__all__=['User', 'Permission', 'Group', 'NotAuthenticated']