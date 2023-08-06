# -*- coding: utf-8 -*-
from zope.interface import implements
from repoze.who.interfaces import IAuthenticator
from repoze.who.interfaces import IMetadataProvider
from repoze.what.adapters import BaseSourceAdapter, SourceError
from couchdbkit import Server, contain
from couchdbkit.loaders import FileSystemDocsLoader
from documents import Group, Permission, User
import os


class Base(object):

    def __init__(self, db, klass=None):
        self.db = db
        if klass is not None:
            self.klass = klass
        contain(db, self.klass)


class GroupAdapter(Base, BaseSourceAdapter):
    """Group adapter. klass must be a couchdbkit.Document named Group.
    Default to :class:`~repoze.what.plugins.couchdbkit.documents.Group`
    """

    klass = Group

    def _get_all_sections(self):
        groups = self.klass.view('group/all')
        return [{g._id:[]} for g in groups]

    def _get_section_items(self, section):
        users = self.klass.view('group/users', key=section)
        return [doc._id for doc in users]

    def _find_sections(self, hint):
        user = self.db.get(hint['repoze.what.userid'])
        groups = [doc['_id'] for doc in user.get('groups', [])]
        return groups

    def _include_items(self, section, items):
        raise NotImplementedError()

    def _item_is_included(self, section, item):
        user = self.db.get(item)
        groups = [doc['_id'] for doc in user.get('groups', [])]
        return section in groups

    def _section_exists(self, section):
        try:
            self.db.get(section)
            return True
        except:
            return False

class PermissionAdapter(Base, BaseSourceAdapter):
    """Permission adapter. klass must be a couchdbkit.Document named Permission.
    Default to :class:`~repoze.what.plugins.couchdbkit.documents.Permission`
    """
    klass = Permission

    def _get_all_sections(self):
        raise NotImplementedError()

    def _get_section_items(self, section):
        raise NotImplementedError()

    def _find_sections(self, hint):
        group = self.db.get(hint)
        perms = [doc['name'] for doc in group.get('permissions', [])]
        return perms

    def _include_items(self, section, items):
        raise NotImplementedError()

    def _item_is_included(self, section, item):
        raise NotImplementedError()

    def _section_exists(self, section):
        raise NotImplementedError()

class Authenticator(Base):
    """Authenticator plugin. klass must be a couchdbkit.Document named User.
    Default to :class:`~repoze.what.plugins.couchdbkit.documents.User`
    """
    implements(IAuthenticator)
    klass = User

    def authenticate(self, environ, identity):
        login = identity.get('login', '')
        password = identity.get('password', '')
        if login:
            user = self.klass.authenticate(login, password)
            if user is not None:
                identity['login'] = str(user.username)
                return user._id

class MDPlugin(Base):
    """Metadata provider plugin. klass must be a couchdbkit.Document named User.
    Default to :class:`~repoze.what.plugins.couchdbkit.documents.User`
    """
    implements(IMetadataProvider)
    klass = User

    def add_metadata(self, environ, identity):
        uid = identity['repoze.who.userid']
        if uid:
            user = self.klass.get(uid)
            identity['user'] = user

def init_design(db):
    design_docs = os.path.join(os.path.dirname(__file__), '_design')
    loader = FileSystemDocsLoader(design_docs)
    loader.sync(db, verbose=True)

