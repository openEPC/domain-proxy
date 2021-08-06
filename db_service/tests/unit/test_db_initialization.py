from parameterized import parameterized

from db_service.db_initialize import DBInitializer
from db_service.models import DBRequestState, DBRequestType, DBCbsdState, DBGrantState
from db_service.session_manager import SessionManager
from db_service.tests.db_testcase import DBTestCase


class DBInitializationTestCase(DBTestCase):

    def setUp(self):
        super().setUp()
        self.initializer = DBInitializer(SessionManager(db_engine=self.engine))

    @parameterized.expand([
        (DBRequestType, 6),
        (DBRequestState, 2),
        (DBGrantState, 3),
        (DBCbsdState, 2),
    ])
    def test_db_is_initialized_with_db_states_and_types(self, model, expected_post_init_count):
        # Given
        model_entities_pre_init = self.session.query(model).all()

        # When
        self.initializer.initialize()

        model_entities_post_init = self.session.query(model).all()

        # Then
        self.assertEqual(0, len(model_entities_pre_init))
        self.assertEqual(expected_post_init_count, len(model_entities_post_init))

    @parameterized.expand([
        (DBRequestType, ),
        (DBRequestState, ),
        (DBGrantState, ),
        (DBCbsdState, ),
    ])
    def test_db_is_initialized_only_once(self, model):
        # Given / When
        self.initializer.initialize()
        model_entities_post_init_1 = self.session.query(model).all()

        self.initializer.initialize()
        model_entities_post_init_2 = self.session.query(model).all()

        # Then
        self.assertListEqual(model_entities_post_init_1, model_entities_post_init_2)
