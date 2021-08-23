import json
from time import sleep

from active_mode_pb2 import ToggleActiveModeParams
from db_service.config import TestConfig
from db_service.db_initialize import DBInitializer
from db_service.models import Base, DBCbsd
from db_service.session_manager import SessionManager
from db_service.tests.db_testcase import DBTestCase
from mappings.types import CbsdStates, Switch
from radio_controller.services.active_mode_controller.service import ActiveModeControllerService, cbsd_state_mapping
from radio_controller.services.radio_controller.service import RadioControllerService
from requests_pb2 import RequestPayload


class ActiveModeControllerTestCase(DBTestCase):

    def setUp(self):
        super().setUp()
        Base.metadata.drop_all()
        Base.metadata.create_all()
        DBInitializer(SessionManager(self.engine)).initialize()
        self.amc_service = ActiveModeControllerService(SessionManager(self.engine))
        self.rc_service = RadioControllerService(SessionManager(self.engine))

    def get_config(self):
        return TestConfig()

    def test_cbsd_auto_registered(self):
        # Given
        registration_request = {
            "registrationRequest": [
                {
                    "fccId": "foo",
                    "cbsdCategory": "B",
                    "callSign": "WSD987",
                    "userId": "John Doe",
                    "airInterface": {
                        "radioTechnology": "E_UTRA"
                    },
                    "cbsdSerialNumber": "4321dcba",
                    "measCapability": [
                        "RECEIVED_POWER_WITHOUT_GRANT"
                    ],
                    "installationParam": {
                        "latitude": 37.425056,
                        "longitude": -122.084113,
                        "height": 9.3,
                        "heightType": "AGL",
                        "indoorDeployment": False,
                        "antennaAzimuth": 271,
                        "antennaDowntilt": 3,
                        "antennaGain": 16,
                        "antennaBeamwidth": 30
                    },
                    "groupingParam": [
                        {
                            "groupId": "example-group-3",
                            "groupType": "INTERFERENCE_COORDINATION"
                        }
                    ]
                }
            ]
        }

        self.rc_service.UploadRequests(RequestPayload(payload=json.dumps(registration_request)), None)

        cbsd = self.session.query(DBCbsd).first()
        self.session.commit()

        # When
        self.amc_service.ToggleActiveMode(ToggleActiveModeParams(
            cbsd_id=cbsd.id,
            switch=Switch.ON.value,
            desired_state=cbsd_state_mapping[CbsdStates.REGISTERED.value]),
            None
        )

        sleep(200)

        self.session.commit()

        cbsd = self.session.query(DBCbsd).first()

        # Then
        self.assertEqual(CbsdStates.REGISTERED.value, cbsd.state.name)
        self.assertEqual(1, len(cbsd.channels))
        self.assertEqual(1, len(cbsd.grants))
