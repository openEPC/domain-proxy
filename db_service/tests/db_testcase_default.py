import unittest

from sqlalchemy import create_engine

from db_service.config import TestConfig
from db_service.models import Base
from db_service.session_manager import Session


class DBTestCaseDefault(unittest.TestCase):

    @staticmethod
    def get_config():
        return TestConfig()

    def setUp(self):
        config = self.get_config()
        self.engine = create_engine(
            url=config.SQLALCHEMY_DB_URI,
            encoding=config.SQLALCHEMY_DB_ENCODING,
            echo=False,
            future=config.SQLALCHEMY_FUTURE
        )
        self.session = Session()
        Base.metadata.bind = self.engine
        Base.metadata.create_all()

    def tearDown(self):
        self.session.rollback()
        self.session.close()
