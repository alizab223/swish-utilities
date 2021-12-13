import json
from unittest import TestCase
from pandas.io.parsers import read_csv
import requests_mock
from run import cli
from cli_util import DipException
from tests.common import SNOW_RESPONSE1, SNOW_RESPONSE_WITH_CUSTOM_ID, UNITEST_OUTPUT_FILE, UNITEST_OUTPUT_FILE_PREFIX, patch_for_tests
import os
import os.path
from click.testing import CliRunner

patch_for_tests()


class FilteringTestCase(TestCase):

    def setUp(self) -> None:
        if os.path.isfile(UNITEST_OUTPUT_FILE):
            os.remove(UNITEST_OUTPUT_FILE)
        if os.path.isfile(f'{UNITEST_OUTPUT_FILE_PREFIX}_1.json'):
            os.remove(f'{UNITEST_OUTPUT_FILE_PREFIX}_1.json')

    def test_config_auth(self):
        assert not os.path.isfile(
            UNITEST_OUTPUT_FILE), "The file should be deleted"
        mock_session = requests_mock.Mocker()
        mock_session.register_uri(requests_mock.ANY,
                                  'https://dev71074.service-now.com/api/now/table/sys_audit',
                                  text=SNOW_RESPONSE1)
        mock_session.start()

        args = ["--extract", "--url", "https://dev71074.service-now.com/api/now/table/sys_audit?sysparm_query=tablename=incident",
                "--batch_size", "10000", "--file_limit", "50000",
                "--start_date", "2021-10-03", "--end_date", "2021-10-04"]
        runner = CliRunner()
        with self.assertRaises(Exception) as context:
            result = runner.invoke(cli, args, catch_exceptions=False)
            print(result.output)

        self.assertTrue(isinstance(context.exception, DipException))

        args.append('--auth_file')
        args.append('tests/data/fake_auth.json')

        result = runner.invoke(cli, args, catch_exceptions=False)
        print(result.output)
        assert result.exit_code == 0