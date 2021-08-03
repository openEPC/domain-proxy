import testing.postgresql

from db_service.db_initialize import DBInitializer
from db_service.models import DBCbsd, DBCbsdState, DBGrant, DBGrantState, DBActiveModeConfig, DBChannel
from db_service.session_manager import SessionManager
from db_service.tests.db_testcase import DBTestCase
from radio_controller.services.active_mode_controller.service import ActiveModeControllerService
import active_mode_pb2 as active_mode
from mappings.types import CbsdStates, GrantStates

Postgresql = testing.postgresql.PostgresqlFactory(cache_initialized_db=True)

class ActiveModeControllerTestCase(DBTestCase):
    def setUp(self):
        super().setUp()
        self.amc_service = ActiveModeControllerService(SessionManager(self.engine))
        DBInitializer(SessionManager(self.engine)).initialize()

    def test_get_state(self):
        # given
        unregistered_state = DBCbsdState(name=CbsdStates.UNREGISTERED.value)
        registered_state = DBCbsdState(name=CbsdStates.REGISTERED.value)

        idle_state = DBGrantState(name=GrantStates.IDLE.value)
        granted_state = DBGrantState(name=GrantStates.GRANTED.value)
        authorized_state = DBGrantState(name=GrantStates.AUTHORIZED.value)

        some_cbsd = DBCbsd(
            id=1,
            state=registered_state,
            cbsd_id="some_cbsd_id",
            user_id="some_user_id",
            fcc_id="some_fcc_id",
            cbsd_serial_number="some_serial_number",
            eirp_capability=1.23,
        )
        other_cbsd = DBCbsd(
            id=2,
            state=registered_state,
            cbsd_id="other_cbsd_id",
            user_id="other_user_id",
            fcc_id="other_fcc_id",
            cbsd_serial_number="other_serial_number",
        )
        cbsd_without_active_mode = DBCbsd(
            id=3,
            state=registered_state,
            cbsd_id="cbsd_without_active_mode_id"
        )
        some_active_mode_config = DBActiveModeConfig(
            id=1,
            cbsd_id=some_cbsd.id,
            desired_state=registered_state,
        )
        other_active_mode_config = DBActiveModeConfig(
            id=2,
            cbsd_id=other.id,
            desired_state=registered_state,
        )
        some_channels = _
        expected_state = active_mode.State(
            active_mode_configs = [
                active_mode.ActiveModeConfig(
                    desired_state=active_mode.Registered,
                    cbsd=active_mode.Cbsd(
                        id="some_cbsd_id",
                        user_id="some_user_id",
                        fcc_id="some_fcc_id",
                        serial_number="some_serial_number",
                        state=active_mode.Registered,
                        grants=[
                            active_mode.Grant(
                                id="some_granted_grant_id",
                                state=active_mode.Granted,
                                heartbeat_interval_sec = 100,
                                last_heartbeat_timestamp=200,
                            ),
                            active_mode.Grant(
                                id="some_authorized_grant_id",
                                state=active_mode.Authorized,
                                heartbeat_interval_sec = 300,
                                last_heartbeat_timestamp=400,
                            ),
                        ],
                        channels=[
                            active_mode.Channel(
                                frequency_range = active_mode.FrequencyRange(
                                    low = 50,
                                    high = 60,
                                ),
                                max_eirp = 24.5,
                                last_eirp = 25.5,
                            ),
                            active_mode.Channel(
                                frequency_range=active_mode.FrequencyRange(
                                    low=70,
                                    high=80,
                                ),
                            ),
                        ],
                        eirp_capability=26.5,
                    ),
                ),
                active_mode.ActiveModeConfig(
                    desired_state = active_mode.Unregistered,
                    cbsd = active_mode.Cbsd(
                        id="other_cbsd_id",
                        state=active_mode.Unregistered,
                    )
                ),
            ]
        )
        actual_state = self.amc_service.GetState(active_mode.GetStateRequest(), None)

        # Then
        self.assertEqual(expected_state, actual_state)
