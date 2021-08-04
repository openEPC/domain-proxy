import testing.postgresql
from datetime import datetime

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
        # Given
        grant_states = {x.name: x.id for x in self.session.query(DBGrantState).all()}

        unregistered_state = DBCbsdState(name=CbsdStates.UNREGISTERED.value)
        registered_state = DBCbsdState(name=CbsdStates.REGISTERED.value)

        some_cbsd = DBCbsd(
            id=1,
            state=registered_state,
            cbsd_id="some_cbsd_id",
            user_id="some_user_id",
            fcc_id="some_fcc_id",
            cbsd_serial_number="some_serial_number",
            eirp_capability=26.5,
        )
        other_cbsd = DBCbsd(
            id=2,
            state=unregistered_state,
            cbsd_id="other_cbsd_id",
        )
        cbsd_without_active_mode = DBCbsd(
            id=3,
            state=registered_state,
            cbsd_id="cbsd_without_active_mode_id"
        )
        cbsds = [some_cbsd, other_cbsd, cbsd_without_active_mode]
        active_mode_configs = [
            DBActiveModeConfig(
                id=1,
                cbsd_id=some_cbsd.id,
                desired_state=registered_state,
            ),
            DBActiveModeConfig(
                id=2,
                cbsd_id=other_cbsd.id,
                desired_state=unregistered_state,
            ),
        ]
        grants = [
            DBGrant(
                id=1,
                state_id=grant_states[GrantStates.IDLE.value],
                cbsd_id=some_cbsd.id,
                grant_id="some_idle_grant_id",
            ),
            DBGrant(
                id=2,
                state_id=grant_states[GrantStates.GRANTED.value],
                cbsd_id=some_cbsd.id,
                grant_id="some_granted_grant_id",
                heartbeat_interval=100,
                last_heartbeat_request_time=datetime.fromtimestamp(200),
            ),
            DBGrant(
                id=3,
                state_id=grant_states[GrantStates.AUTHORIZED.value],
                cbsd_id=some_cbsd.id,
                grant_id="some_authorized_grant_id",
                heartbeat_interval=300,
                last_heartbeat_request_time=datetime.fromtimestamp(400),
            ),
        ]
        channels = [
            DBChannel(
                id=1,
                cbsd_id=some_cbsd.id,
                low_frequency=50,
                high_frequency=60,
                max_eirp=24.5,
                last_used_max_eirp=25.5,
                channel_type="some channel type",
                rule_applied="some rule",
            ),
            DBChannel(
                id=2,
                cbsd_id=some_cbsd.id,
                low_frequency=70,
                high_frequency=80,
                channel_type="some channel type",
                rule_applied="some rule",
            )
        ]
        resources = [r for l in [cbsds, active_mode_configs, grants, channels] for r in l]
        self.session.add_all(resources)
        self.session.commit()

        # When
        actual_state = self.amc_service.GetState(active_mode.GetStateRequest(), None)

        # Then
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
        self.assertEqual(expected_state, actual_state) # TODO do something, so that diff is not truncated
