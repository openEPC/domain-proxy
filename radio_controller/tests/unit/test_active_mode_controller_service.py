import testing.postgresql

from db_service.db_initialize import DBInitializer
from db_service.session_manager import SessionManager
from db_service.tests.db_testcase import DBTestCase
from radio_controller.services.active_mode_controller.service import ActiveModeControllerService

Postgresql = testing.postgresql.PostgresqlFactory(cache_initialized_db=True)

class ActiveModeControllerTestCase(DBTestCase):
    def setUp(self):
        super().setUp()
        self.amc_service = ActiveModeControllerService(SessionManager(self.engine))
        DBInitializer(SessionManager(self.engine)).initialize()

    def test_get_state(self):
        pass
