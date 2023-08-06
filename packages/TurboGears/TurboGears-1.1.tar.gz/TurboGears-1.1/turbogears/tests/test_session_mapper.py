"""Unit tests for turbogears.database.session_mapper."""

import unittest

from sqlalchemy import Table, Column, Integer, String
from sqlalchemy.orm import clear_mappers

from turbogears import config
from turbogears.database import (bind_metadata, metadata,
    session, session_mapper, set_db_uri)


class User(object):
    pass

class TestSessionMapper(unittest.TestCase):

    def setUp(self):
        """Set database configuration and set up database.
        """
        self.sa_dburi = config.get('sqlalchemy.dburi')
        set_db_uri('sqlite:///:memory:', 'sqlalchemy')
        bind_metadata()
        self.users_table = Table("users", metadata,
            Column("user_id", Integer, primary_key=True),
            Column("user_name", String(40)),
            Column("password", String(10)))

    def tearDown(self):
        """Clear database configuration and drop database.
        """
        try:
            session.expunge_all()
        except:
            session.clear()
        clear_mappers()
        metadata.drop_all()
        metadata.clear()
        set_db_uri(self.sa_dburi, 'sqlalchemy')

    def test_query_attribute(self):
        """Object mapped with session-aware mapper have 'query' attribute."""
        session_mapper(User, self.users_table)
        assert hasattr(User, 'query')
        assert hasattr(User.query, 'filter')

    def test_contructor(self):
        """Mapped objects have constructor which takes attributes as kw args."""
        session_mapper(User, self.users_table)
        metadata.create_all()
        test_user = User(user_id=1, user_name='test', password='secret')
        assert test_user.user_name == 'test'

    def test_validate(self):
        """Constructor of mapped objects validates kw args."""
        session_mapper(User, self.users_table)
        metadata.create_all()
        u = User(non_existant_attr='foo')
        assert u.non_existant_attr == 'foo'
        clear_mappers()
        metadata.drop_all()
        session_mapper(User, self.users_table, validate=True)
        metadata.create_all()
        self.assertRaises(TypeError, User, non_existant_attr='foo')

    def test_autoadd(self):
        """Mapped objects are automatically added to session."""
        session_mapper(User, self.users_table, autoadd=True)
        metadata.create_all()
        test_user = User(user_id=1, user_name='test', password='secret')
        assert test_user in session

    def test_save_on_init(self):
        """'save_on_init' can be used as alias for 'autoadd' mapper kwarg."""
        session_mapper(User, self.users_table, save_on_init=True)
        metadata.create_all()
        test_user = User(user_id=1, user_name='test', password='secret')
        assert test_user in session
