# -*- coding: utf-8 -*-
from couchdbkit import schema
from couchdbkit import Document
try:
    from hashlib import sha1
except:
    from sha import new as sha1

def encrypt_value(value):
    return sha1(value).hexdigest()


class Permission(Document):
    name = schema.StringProperty(required=True)

class Group(Permission):
    permissions = schema.SchemaListProperty(Permission)

class User(Document):
    username = schema.StringProperty(required=True)
    password = schema.StringProperty(required=True)
    password_check = schema.StringProperty(required=True)
    groups = schema.SchemaListProperty(Group)
    active = schema.BooleanProperty()

    @classmethod
    def authenticate(cls, username, password):
        """Use view ``auth/user_by_name`` to check authentification.
        Return a :class:`~repoze.what.plugins.couchdbkit.documents.User` object on success.
        """
        users = cls.view('auth/user_by_name', key=username)
        for user in users:
            if user and user.active and encrypt_value(password) == user.password:
                return user
            break

    def encrypt_password(self):
        """Encrypt password whith sha1 if not already done"""
        if self.password and self.password != self.password_check:
            self.password = encrypt_value(self.password)
            self.password_check = self.password

